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

NS = 'starfleet-031-010-01-02'

def only_this_namespace(peer, namespace):
    """A peer without a namespaceSelector stays in the policy's namespace; with one, it must match only that namespace."""
    if 'namespaceSelector' not in peer:
        return True
    items = json.loads(kubectl('get', 'namespace', '-o', 'json'))['items']
    matched = [item['metadata']['name'] for item in items if selector_matches(peer['namespaceSelector'], item['metadata'].get('labels') or {})]
    return matched == [namespace]

def scanner_rules():
    selector = get('networkpolicy', 'scanner-egress', NS)['spec'].get('podSelector')
    assert selector_matches(selector, pod_labels(NS, 'scanner')), 'scanner-egress must select the scanner pod'
    for labels in (pod_labels(NS, 'decoy'), pod_labels(NS, 'idler'), {'app': 'archive'}):
        assert not selector_matches(selector, labels), 'scanner-egress must select only the scanner pod, not ' + labels.get('app', 'other pods')
    rules = rules_for(NS, pod_labels(NS, 'scanner'), 'Egress')
    assert rules, 'The scanner pod needs egress rules'
    no_open_rules(rules)
    return rules

def is_dns_peer(peer):
    """One peer entry that selects only the kube-dns pods in kube-system."""
    if 'namespaceSelector' not in peer or 'podSelector' not in peer:
        return False
    return (selector_matches(peer['namespaceSelector'], {'kubernetes.io/metadata.name': 'kube-system'})
            and not selector_matches(peer['namespaceSelector'], {'kubernetes.io/metadata.name': 'default'})
            and selector_matches(peer['podSelector'], {'k8s-app': 'kube-dns'})
            and not selector_matches(peer['podSelector'], {'k8s-app': 'other'}))

if wants('scanner-egress-policy'):
    rules = scanner_rules()
    dns_rules = [rule for rule in rules if peers_of(rule) and all(is_dns_peer(peer) for peer in peers_of(rule))]
    assert dns_rules and any({('UDP', '53', None), ('TCP', '53', None)} <= port_set(rule) for rule in dns_rules), 'Allow UDP 53 and TCP 53 to the kube-dns pods in kube-system'
    for rule in dns_rules:
        assert port_set(rule) <= {('UDP', '53', None), ('TCP', '53', None)}, 'The DNS rule must allow only port 53'
    app_rules = [rule for rule in rules if rule not in dns_rules]
    assert app_rules, 'Add a rule for the archive pods'
    for rule in app_rules:
        assert port_set(rule) == {('TCP', '8080', None)}, 'The archive rule must allow only TCP 8080, the pod port'
        for peer in peers_of(rule):
            assert 'ipBlock' not in peer and selector_matches(peer.get('podSelector'), {'app': 'archive'}), 'The archive rule must select the archive pods by label'
            assert not selector_matches(peer.get('podSelector'), pod_labels(NS, 'decoy')), 'The archive rule must not select the decoy pod'
            assert only_this_namespace(peer, NS), 'The archive rule must select pods in ' + NS + ' only'
if wants('scanner-reaches-archive'):
    scanner_rules()
    output = client(NS, 'scanner', 'dns', 'archive.' + NS + '.svc.cluster.local')
    assert output == 'resolved ' + service_ip(NS, 'archive'), 'The scanner pod must resolve the archive Service name but got: ' + output
    expect_open(NS, 'scanner', service_ip(NS, 'archive'), 80, note='through the Service ')
if wants('decoy-blocked'):
    scanner_rules()
    expect_blocked(NS, 'scanner', pod_ip(NS, 'decoy'), 8080)
    expect_open(NS, 'idler', pod_ip(NS, 'decoy'), 8080, note='(the decoy must stay healthy and reachable for other pods) ')
