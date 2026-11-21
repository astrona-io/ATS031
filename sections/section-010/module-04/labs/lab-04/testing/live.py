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

NS, OUTPOST = 'starfleet-031-010-04-04', 'outpost-031-010-04-04'
ROWS = [('rover-to-hangar', 'starfleet-031-010-04-04', 'rover', 'starfleet-031-010-04-04', 'hangar'), ('rover-to-vault', 'starfleet-031-010-04-04', 'rover', 'starfleet-031-010-04-04', 'vault'), ('tanker-to-hangar', 'starfleet-031-010-04-04', 'tanker', 'starfleet-031-010-04-04', 'hangar'), ('drone-to-hangar', 'outpost-031-010-04-04', 'drone', 'starfleet-031-010-04-04', 'hangar'), ('drone-to-vault', 'outpost-031-010-04-04', 'drone', 'starfleet-031-010-04-04', 'vault')]
BASELINE = {
    'default-deny-all': {'podSelector': {}, 'policyTypes': ['Ingress', 'Egress']},
    'hangar-ingress': {'podSelector': {'matchLabels': {'app': 'hangar'}}, 'policyTypes': ['Ingress'], 'ingress': [{'from': [{'podSelector': {'matchLabels': {'app': 'rover'}}}, {'namespaceSelector': {'matchLabels': {'kubernetes.io/metadata.name': OUTPOST}}}], 'ports': [{'protocol': 'TCP', 'port': 8080}]}]},
    'rover-egress': {'podSelector': {'matchLabels': {'app': 'rover'}}, 'policyTypes': ['Egress'], 'egress': [{'to': [{'podSelector': {'matchLabels': {'app': 'hangar'}}}], 'ports': [{'protocol': 'TCP', 'port': 8080}]}, {'to': [{'namespaceSelector': {'matchLabels': {'kubernetes.io/metadata.name': 'kube-system'}}, 'podSelector': {'matchLabels': {'k8s-app': 'kube-dns'}}}], 'ports': [{'protocol': 'UDP', 'port': 53}, {'protocol': 'TCP', 'port': 53}]}]},
}
DNS_ROWS = [('rover-dns', 'starfleet-031-010-04-04', 'rover'), ('tanker-dns', 'starfleet-031-010-04-04', 'tanker')]

def recorded():
    names = sorted(item['metadata']['name'] for item in policies(NS))
    assert names == ['default-deny-all', 'hangar-ingress', 'rover-egress'], 'Do not change the policies; only record what they do'
    for name, spec in BASELINE.items():
        assert get('networkpolicy', name, NS)['spec'] == spec, 'Do not change the policy ' + name
    assert not policies(OUTPOST), 'Do not create policies in the outpost namespace'
    return get('configmap', 'test-matrix', NS).get('data') or {}

if wants('traffic-rows'):
    data = recorded()
    for key, source_ns, source, target_ns, target in ROWS:
        assert data.get(key) in ('open', 'blocked'), 'Row ' + key + ' must be open or blocked'
        actual = client(source_ns, source, 'tcp', pod_ip(target_ns, target), 8080).split(' ')[0]
        assert data[key] == actual, 'Row ' + key + ' is recorded as ' + data[key] + ' but the request is ' + actual
if wants('dns-rows'):
    data = recorded()
    for key, source_ns, source in DNS_ROWS:
        assert data.get(key) in ('resolved', 'unresolved'), 'Row ' + key + ' must be resolved or unresolved'
        actual = client(source_ns, source, 'dns', 'kubernetes.default.svc.cluster.local').split(' ')[0]
        assert data[key] == actual, 'Row ' + key + ' is recorded as ' + data[key] + ' but the lookup is ' + actual
