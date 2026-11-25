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

NS, OUTPOST, DOCK = 'starfleet-031-010-03-01', 'outpost-031-010-03-01', 'dock-031-010-03-01'

def registry_rules():
    get('networkpolicy', 'registry-from-outpost-courier', NS)
    rules = rules_for(NS, pod_labels(NS, 'registry'), 'Ingress')
    assert rules, 'The registry pod needs an ingress rule'
    no_open_rules(rules)
    return rules

def namespace_labels(name):
    return get('namespace', name, None).get('metadata', {}).get('labels') or {}

if wants('registry-policy'):
    rules = registry_rules()
    for rule in rules:
        assert port_set(rule) == {('TCP', '8080', None)}, 'Admit only TCP 8080'
        for peer in peers_of(rule):
            assert 'namespaceSelector' in peer and 'podSelector' in peer, 'Put the namespaceSelector and the podSelector in the same peer entry'
            assert selector_matches(peer['namespaceSelector'], namespace_labels(OUTPOST)), 'The namespaceSelector must select ' + OUTPOST
            for other in (NS, DOCK):
                assert not selector_matches(peer['namespaceSelector'], namespace_labels(other)), 'The namespaceSelector must not select ' + other
            assert selector_matches(peer['podSelector'], pod_labels(OUTPOST, 'courier')), 'The podSelector must select the courier pod'
            assert not selector_matches(peer['podSelector'], pod_labels(OUTPOST, 'idler')), 'The podSelector must not select the idler pod'
if wants('only-outpost-courier'):
    registry_rules()
    assert [item['metadata']['name'] for item in policies(NS)] == ['registry-from-outpost-courier'], 'Create only the registry-from-outpost-courier policy in ' + NS
    assert not policies(OUTPOST) and not policies(DOCK), 'Do not create policies in ' + OUTPOST + ' or ' + DOCK
    target = pod_ip(NS, 'registry')
    expect_open(OUTPOST, 'courier', target, 8080)
    expect_blocked(OUTPOST, 'idler', target, 8080)
    expect_blocked(DOCK, 'courier', target, 8080)
    expect_blocked(NS, 'courier', target, 8080)
