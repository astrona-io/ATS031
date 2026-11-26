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

NS = 'outpost-031-010-01-04'

def only_this_namespace(peer, namespace):
    """A peer without a namespaceSelector stays in the policy's namespace; with one, it must match only that namespace."""
    if 'namespaceSelector' not in peer:
        return True
    items = json.loads(kubectl('get', 'namespace', '-o', 'json'))['items']
    matched = [item['metadata']['name'] for item in items if selector_matches(peer['namespaceSelector'], item['metadata'].get('labels') or {})]
    return matched == [namespace]

def baseline_intact():
    baseline = get('networkpolicy', 'default-deny-all', NS)['spec']
    assert baseline.get('podSelector') in ({}, None) and sorted(baseline.get('policyTypes', [])) == ['Egress', 'Ingress'], 'default-deny-all must still select every pod for both directions'
    assert not baseline.get('ingress') and not baseline.get('egress'), 'default-deny-all must not allow any traffic'

def depot_rules():
    """The ingress rules that select the depot pod; at least one of them must admit the lander pod."""
    rules = rules_for(NS, pod_labels(NS, 'depot'), 'Ingress')
    lander = pod_labels(NS, 'lander')
    assert any('podSelector' in peer and selector_matches(peer['podSelector'], lander) for rule in rules for peer in peers_of(rule)), 'No ingress rule on the depot pod admits the lander pod'
    return rules

if wants('lander-reaches-depot'):
    baseline_intact()
    depot_rules()
    expect_open(NS, 'lander', pod_ip(NS, 'depot'), 8080)
if wants('baseline-and-narrow-rules'):
    baseline_intact()
    depot = depot_rules()
    names = sorted(item['metadata']['name'] for item in policies(NS))
    assert names == ['default-deny-all', 'depot-ingress', 'lander-egress'], 'Repair depot-ingress in place: keep exactly the policies default-deny-all, depot-ingress and lander-egress'
    lander_rules = rules_for(NS, pod_labels(NS, 'lander'), 'Egress')
    no_open_rules(lander_rules)
    for rule in lander_rules:
        assert port_set(rule) == {('TCP', '8080', None)}, 'lander-egress must still allow only TCP port 8080'
        for peer in peers_of(rule):
            assert 'podSelector' in peer and 'ipBlock' not in peer and only_this_namespace(peer, NS), 'lander-egress must still select the depot pod in ' + NS
            assert not selector_matches(peer['podSelector'], pod_labels(NS, 'stray')), 'lander-egress must not select the stray pod'
    no_open_rules(depot)
    for rule in depot:
        assert port_set(rule) == {('TCP', '8080', None)}, 'The depot ingress rule must allow only TCP port 8080'
        for peer in peers_of(rule):
            assert 'podSelector' in peer and 'ipBlock' not in peer and only_this_namespace(peer, NS), 'Admit the lander pod with a podSelector in the same namespace'
            assert selector_matches(peer['podSelector'], pod_labels(NS, 'lander')), 'The peer must select the lander pod'
            assert not selector_matches(peer['podSelector'], pod_labels(NS, 'stray')), 'The peer must not select the stray pod'
if wants('other-paths-blocked'):
    baseline_intact()
    depot_rules()
    expect_blocked(NS, 'stray', pod_ip(NS, 'depot'), 8080)
    expect_blocked(NS, 'lander', pod_ip(NS, 'stray'), 8080)
