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

NS = 'starfleet-031-010-03-06'

def kiosk_ips():
    pods = json.loads(kubectl('-n', NS, 'get', 'pods', '-l', 'app=kiosk', '-o', 'json'))['items']
    addresses = [item['status'].get('podIP') for item in pods if item['status'].get('phase') == 'Running']
    assert len(addresses) == 2 and all(addresses), 'Both kiosk replicas must be running'
    return addresses

def kiosk_rules():
    get('networkpolicy', 'kiosk-ingress', NS)
    assert sorted(item['metadata']['name'] for item in policies(NS)) == ['default-deny-ingress', 'kiosk-ingress'], 'Repair kiosk-ingress in place and add no other policy'
    baseline = get('networkpolicy', 'default-deny-ingress', NS)['spec']
    assert baseline.get('podSelector') in ({}, None) and baseline.get('policyTypes') == ['Ingress'] and not baseline.get('ingress'), 'Keep default-deny-ingress as it is'
    rules = rules_for(NS, {'app': 'kiosk'}, 'Ingress')
    no_open_rules(rules)
    return rules

if wants('service-port-repaired'):
    rules = kiosk_rules()
    for rule in rules:
        assert ('TCP', '80', None) not in port_set(rule), 'Port 80 is the Service port; the pods receive the request on 8080'
    for address in kiosk_ips():
        expect_open(NS, 'visitor', address, 8080)
    expect_open(NS, 'visitor', service_ip(NS, 'kiosk'), 80, note='through the Service ')
if wants('metrics-range'):
    rules = kiosk_rules()
    ports = set()
    for rule in rules:
        ports |= port_set(rule)
    assert ('TCP', '9100', 9102) in ports, 'Allow TCP 9100 to 9102 with one item that has port: 9100 and endPort: 9102'
    assert ports <= {('TCP', '8080', None), ('TCP', 'http', None), ('TCP', '9100', 9102)}, 'Allow only TCP 8080 and the range 9100 to 9102'
    for address in kiosk_ips():
        for port in (9100, 9102):
            expect_open(NS, 'collector', address, port)
        expect_blocked(NS, 'visitor', address, 9101, note='(the range is for the collector only) ')
        expect_blocked(NS, 'collector', address, 8080, note='(the collector needs only the metrics ports) ')
