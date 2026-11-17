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

HOME, OUTPOST, POD_RANGE = 'starfleet-031-010-03-04', 'outpost-031-010-03-04', ipaddress.ip_network('192.168.0.0/16')

def ip_blocks():
    get('networkpolicy', 'ledger-from-pod-range', HOME)
    rules = rules_for(HOME, pod_labels(HOME, 'ledger'), 'Ingress')
    assert rules, 'The ledger pod needs an ingress rule'
    no_open_rules(rules)
    found = []
    for rule in rules:
        assert port_set(rule) == {('TCP', '7070', None)}, 'The ledger rule must allow only TCP port 7070'
        for peer in peers_of(rule):
            assert set(peer) == {'ipBlock'}, 'Use an ipBlock peer only'
            found.append(peer['ipBlock'])
    return found

if wants('range-admits-courier'):
    blocks = ip_blocks()
    assert any(ipaddress.ip_network(block['cidr'], strict=False).subnet_of(POD_RANGE) and ipaddress.ip_address(pod_ip(OUTPOST, 'courier')) in ipaddress.ip_network(block['cidr'], strict=False) for block in blocks), 'The ipBlock cidr must lie inside the pod range and contain the courier address'
    expect_open(OUTPOST, 'courier', pod_ip(HOME, 'ledger'), 7070)
if wants('except-blocks-rogue'):
    blocks = ip_blocks()
    rogue = ipaddress.ip_address(pod_ip(OUTPOST, 'rogue'))
    courier = ipaddress.ip_address(pod_ip(OUTPOST, 'courier'))
    for block in blocks:
        excluded = [ipaddress.ip_network(item, strict=False) for item in block.get('except') or []]
        if rogue in ipaddress.ip_network(block['cidr'], strict=False):
            assert any(rogue in network for network in excluded), 'An except entry must remove the rogue address'
        assert not any(courier in network for network in excluded), 'The except list must not remove the courier address'
        assert all(network.prefixlen == 32 for network in excluded), 'Remove exactly one address with a /32 entry'
    expect_blocked(OUTPOST, 'rogue', pod_ip(HOME, 'ledger'), 7070)
    expect_open(OUTPOST, 'courier', pod_ip(HOME, 'ledger'), 7070)
