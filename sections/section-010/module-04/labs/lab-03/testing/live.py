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

NS = 'starfleet-031-010-04-03'

def endpoint():
    slices = json.loads(kubectl('-n', 'default', 'get', 'endpointslice', '-l', 'kubernetes.io/service-name=kubernetes', '-o', 'json'))['items']
    return slices[0]['endpoints'][0]['addresses'][0], slices[0]['ports'][0]['port']

def operator_rules():
    get('networkpolicy', 'operator-to-api-server', NS)
    address, port = endpoint()
    rules = [rule for rule in rules_for(NS, pod_labels(NS, 'operator'), 'Egress') if ('UDP', '53', None) not in port_set(rule)]
    assert rules, 'The operator pod needs an egress rule to the API server'
    no_open_rules(rules)
    return rules, address, port

if wants('operator-reaches-api'):
    rules, address, port = operator_rules()
    assert any(ipaddress.ip_address(address) in ipaddress.ip_network(peer['ipBlock']['cidr'], strict=False) for rule in rules for peer in peers_of(rule) if 'ipBlock' in peer), 'An ipBlock must contain the API server endpoint address ' + address
    assert any(('TCP', str(port), None) in port_set(rule) for rule in rules), 'Allow the endpoint port ' + str(port) + ', not the Service port 443'
    expect_open(NS, 'operator', service_ip('default', 'kubernetes'), 443, note='through the kubernetes Service ')
if wants('api-rule-narrow'):
    rules, address, port = operator_rules()
    for rule in rules:
        assert port_set(rule) == {('TCP', str(port), None)}, 'Allow only TCP port ' + str(port)
        for peer in peers_of(rule):
            assert set(peer) == {'ipBlock'} and peer['ipBlock']['cidr'] == address + '/32', 'Use one ipBlock with the cidr ' + address + '/32'
    assert not selector_matches(get('networkpolicy', 'operator-to-api-server', NS)['spec'].get('podSelector'), pod_labels(NS, 'helper')), 'The policy must not select the helper pod'
    expect_blocked(NS, 'helper', service_ip('default', 'kubernetes'), 443)
    expect_blocked(NS, 'operator', pod_ip(NS, 'helper'), 8080)
    expect_dns(NS, 'helper')
