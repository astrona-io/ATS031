# Shared helpers for this lab's live checks. check.py runs this file in its own
# globals, so wants(), kubectl(), get() and command() are available here.
import ipaddress
import json


def policies(namespace):
    return json.loads(kubectl('-n', namespace, 'get', 'networkpolicy', '-o', 'json'))['items']


def selector_matches(selector, labels):
    """Apply a Kubernetes label selector (matchLabels and matchExpressions)."""
    selector = selector or {}
    for key, value in (selector.get('matchLabels') or {}).items():
        if labels.get(key) != value:
            return False
    for expression in selector.get('matchExpressions') or []:
        key, operator, values = expression['key'], expression['operator'], expression.get('values') or []
        if operator == 'In' and labels.get(key) not in values:
            return False
        if operator == 'NotIn' and key in labels and labels[key] in values:
            return False
        if operator == 'Exists' and key not in labels:
            return False
        if operator == 'DoesNotExist' and key in labels:
            return False
    return True


def pod_labels(namespace, name):
    return get('pod', name, namespace)['metadata'].get('labels', {})


def selecting(namespace, labels, direction):
    """The policies in a namespace that select these pod labels for one direction."""
    return [policy for policy in policies(namespace)
            if selector_matches(policy['spec'].get('podSelector'), labels) and direction in policy['spec'].get('policyTypes', [])]


def rules_for(namespace, labels, direction):
    found = []
    for policy in selecting(namespace, labels, direction):
        found += policy['spec'].get(direction.lower()) or []
    return found


def port_set(rule):
    """The ports of a rule as an order-independent set of (protocol, port, endPort)."""
    return {(item.get('protocol', 'TCP'), str(item.get('port')), item.get('endPort')) for item in rule.get('ports') or []}


def peers_of(rule):
    return (rule.get('to') or []) + (rule.get('from') or [])


def no_open_rules(rules, need_ports=True):
    """Reject rules that reach every pod, every namespace or a wide address range."""
    for rule in rules:
        assert peers_of(rule), 'A rule without peers allows every address'
        for peer in peers_of(rule):
            assert peer, 'An empty peer matches every address'
            if 'namespaceSelector' in peer:
                assert peer['namespaceSelector'], 'namespaceSelector: {} matches every namespace'
            if 'ipBlock' in peer:
                network = ipaddress.ip_network(peer['ipBlock']['cidr'], strict=False)
                assert network.prefixlen >= 16, 'An ipBlock wider than /16 opens too many addresses: ' + peer['ipBlock']['cidr']
        if need_ports:
            assert rule.get('ports'), 'A rule without ports allows every port'


def pod_ip(namespace, name):
    address = get('pod', name, namespace)['status'].get('podIP')
    assert address, f'Pod {name} in {namespace} has no IP address'
    return address


def service_ip(namespace, name):
    return get('service', name, namespace)['spec']['clusterIP']


def client(namespace, pod, *args):
    """Run the lab's test client in a pod: prints open, blocked, refused, resolved or unresolved."""
    result = command(['kubectl', '-n', namespace, 'exec', pod, '--', 'python', '/app/client.py', *[str(item) for item in args]], success=False)
    assert result.returncode == 0, f'The test client could not run in {namespace}/{pod}: ' + (result.stderr.strip().splitlines() or ['no output'])[-1]
    return result.stdout.strip()


def expect_open(namespace, pod, target, port, protocol='tcp', note=''):
    output = client(namespace, pod, protocol, target, port)
    assert output.startswith('open'), f'{namespace}/{pod} must reach {target}:{port}/{protocol.upper()} {note}but got: {output}'
    return output


def expect_blocked(namespace, pod, target, port, protocol='tcp', note=''):
    output = client(namespace, pod, protocol, target, port)
    assert output == 'blocked', f'{namespace}/{pod} must time out to {target}:{port}/{protocol.upper()} {note}but got: {output}'


def expect_dns(namespace, pod, works=True):
    output = client(namespace, pod, 'dns', 'kubernetes.default.svc.cluster.local')
    if works:
        assert output.startswith('resolved'), f'{namespace}/{pod} must resolve names through CoreDNS but got: {output}'
    else:
        assert output == 'unresolved', f'{namespace}/{pod} must not resolve names but got: {output}'

NS, OUTPOST = 'starfleet-031-010-01-01', 'outpost-031-010-01-01'

def only_this_namespace(peer, namespace):
    """A peer without a namespaceSelector stays in the policy's namespace; with one, it must match only that namespace."""
    if 'namespaceSelector' not in peer:
        return True
    items = json.loads(kubectl('get', 'namespace', '-o', 'json'))['items']
    matched = [item['metadata']['name'] for item in items if selector_matches(peer['namespaceSelector'], item['metadata'].get('labels') or {})]
    return matched == [namespace]

def hub_ips():
    pods = json.loads(kubectl('-n', NS, 'get', 'pods', '-l', 'app=hub', '-o', 'json'))['items']
    addresses = [item['status'].get('podIP') for item in pods if item['status'].get('phase') == 'Running']
    assert len(addresses) == 2 and all(addresses), 'Both hub replicas must be running'
    return addresses

def hub_policy():
    policy = get('networkpolicy', 'hub-from-tender', NS)
    spec = policy['spec']
    assert selector_matches(spec.get('podSelector'), {'app': 'hub'}), 'The policy must select the hub pods'
    for name in ('tender', 'idler', 'mirror'):
        assert not selector_matches(spec.get('podSelector'), pod_labels(NS, name)), 'The policy must select only the hub pods, not ' + name
    return spec

if wants('hub-policy'):
    spec = hub_policy()
    assert spec.get('policyTypes') == ['Ingress'], 'The policy must cover ingress only'
    rules = spec.get('ingress') or []
    assert rules, 'The policy needs an ingress rule'
    no_open_rules(rules)
    for rule in rules:
        assert port_set(rule) == {('TCP', '8080', None)} or port_set(rule) == {('TCP', 'http', None)}, 'Allow only TCP port 8080'
        for peer in peers_of(rule):
            assert 'ipBlock' not in peer, 'Admit the pod by its label, not by its address'
            assert selector_matches(peer.get('podSelector'), pod_labels(NS, 'tender')), 'The peer must select the tender pod'
            assert not selector_matches(peer.get('podSelector'), pod_labels(NS, 'idler')), 'The peer must not select the idler pod'
            assert only_this_namespace(peer, NS), 'The peer must select pods in ' + NS + ' only'
if wants('tender-allowed'):
    hub_policy()
    expect_open(NS, 'tender', service_ip(NS, 'hub'), 80, note='through the Service ')
    for address in hub_ips():
        expect_open(NS, 'tender', address, 8080)
if wants('others-denied'):
    hub_policy()
    assert [item['metadata']['name'] for item in policies(NS)] == ['hub-from-tender'], 'Create only the hub-from-tender policy in ' + NS
    assert not policies(OUTPOST), 'Do not create policies in ' + OUTPOST + '; the hub policy alone must cause the block'
    for address in hub_ips():
        expect_blocked(NS, 'idler', address, 8080)
        expect_blocked(OUTPOST, 'stranger', address, 8080)
    expect_open(OUTPOST, 'stranger', pod_ip(NS, 'mirror'), 8080, note='(the stranger pod itself must keep working) ')
    expect_open(NS, 'idler', pod_ip(NS, 'mirror'), 8080, note='(the idler pod itself must keep working) ')
