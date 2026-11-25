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

NS = 'starfleet-031-010-04-02'

def is_dns_peer(peer):
    """One peer entry that selects only the kube-dns pods in kube-system."""
    if 'namespaceSelector' not in peer or 'podSelector' not in peer:
        return False
    return (selector_matches(peer['namespaceSelector'], {'kubernetes.io/metadata.name': 'kube-system'})
            and not selector_matches(peer['namespaceSelector'], {'kubernetes.io/metadata.name': 'default'})
            and selector_matches(peer['podSelector'], {'k8s-app': 'kube-dns'})
            and not selector_matches(peer['podSelector'], {'k8s-app': 'other'}))

def baseline_intact():
    spec = get('networkpolicy', 'default-deny-all', NS)['spec']
    assert spec.get('podSelector') in ({}, None) and sorted(spec.get('policyTypes', [])) == ['Egress', 'Ingress'] and not spec.get('egress') and not spec.get('ingress'), 'Keep default-deny-all unchanged'

def coredns_ip():
    pods = json.loads(kubectl('-n', 'kube-system', 'get', 'pods', '-l', 'k8s-app=kube-dns', '-o', 'json'))['items']
    addresses = [item['status'].get('podIP') for item in pods if item['status'].get('podIP')]
    assert addresses, 'No CoreDNS pod address found'
    return addresses[0]

if wants('navigator-resolves'):
    baseline_intact()
    get('networkpolicy', 'navigator-dns', NS)
    expect_dns(NS, 'navigator')
if wants('dns-only'):
    baseline_intact()
    get('networkpolicy', 'navigator-dns', NS)
    rules = rules_for(NS, pod_labels(NS, 'navigator'), 'Egress')
    assert rules, 'The navigator pod needs an egress rule'
    no_open_rules(rules)
    ports = set()
    for rule in rules:
        assert port_set(rule) <= {('UDP', '53', None), ('TCP', '53', None)}, 'Allow only UDP and TCP port 53'
        assert all(is_dns_peer(peer) for peer in peers_of(rule)), 'Select the kube-system namespace by its name label and the pods by k8s-app: kube-dns in one peer entry'
        ports |= port_set(rule)
    assert ports == {('UDP', '53', None), ('TCP', '53', None)}, 'Allow both UDP 53 and TCP 53'
    for policy in policies(NS):
        if policy['metadata']['name'] != 'navigator-dns':
            assert policy['metadata']['name'] == 'default-deny-all', 'Create only the navigator-dns policy'
    assert not selector_matches(get('networkpolicy', 'navigator-dns', NS)['spec'].get('podSelector'), pod_labels(NS, 'cargo')), 'The DNS policy must not select the cargo pod'
    expect_blocked(NS, 'navigator', coredns_ip(), 9153, note='(the CoreDNS metrics port is not DNS) ')
    expect_blocked(NS, 'navigator', pod_ip(NS, 'cargo'), 8080)
    expect_dns(NS, 'cargo', works=False)
