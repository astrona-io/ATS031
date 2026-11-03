import json

def policies(namespace):
    return json.loads(kubectl('-n', namespace, 'get', 'networkpolicy', '-o', 'json'))['items']

def selects(policy, labels):
    wanted = policy['spec'].get('podSelector', {}).get('matchLabels', {})
    return all(labels.get(key) == value for key, value in wanted.items())

def rules_for(namespace, labels, direction):
    found = []
    for policy in policies(namespace):
        if selects(policy, labels) and direction in policy['spec'].get('policyTypes', []):
            found += policy['spec'].get(direction.lower(), []) or []
    return found

def port_set(rule):
    return {(item.get('protocol', 'TCP'), str(item.get('port')), item.get('endPort')) for item in rule.get('ports', [])}

def peers_of(rule, field):
    return rule.get(field, []) or []

def has_dns_rule(rules):
    wanted = {('UDP', '53', None), ('TCP', '53', None)}
    for rule in rules:
        for peer in peers_of(rule, 'to'):
            if peer.get('podSelector') == {'matchLabels': {'k8s-app': 'kube-dns'}} and peer.get('namespaceSelector') == {'matchLabels': {'kubernetes.io/metadata.name': 'kube-system'}} and wanted <= port_set(rule):
                return True
    return False

def no_open_rules(rules):
    for rule in rules:
        assert rule.get('to') or rule.get('from'), 'A rule without peers allows every address'
        for peer in peers_of(rule, 'to') + peers_of(rule, 'from'):
            assert peer != {} and peer.get('ipBlock', {}).get('cidr') != '0.0.0.0/0', 'A peer matches every address'
        assert rule.get('ports'), 'A rule without ports allows every port'

scout_labels = {'app': 'scout'}
probe_labels = {'app': 'probe'}
egress = rules_for('starfleet', scout_labels, 'Egress')
ingress = rules_for('starfleet', probe_labels, 'Ingress')
no_open_rules(egress)
no_open_rules(ingress)
assert has_dns_rule(egress), 'DNS to CoreDNS on UDP and TCP port 53 is missing'
want_peer = {'namespaceSelector': {'matchLabels': {'kubernetes.io/metadata.name': 'starfleet'}}, 'podSelector': {'matchLabels': {'app': 'probe'}}}
assert any(peer == want_peer and ('TCP', '8080', None) in port_set(rule) for rule in egress for peer in peers_of(rule, 'to')), 'The scout pod needs an egress rule to the probe pods on TCP 8080'
assert any(peer.get('podSelector') == {'matchLabels': {'app': 'scout'}} and ('TCP', '8080', None) in port_set(rule) for rule in ingress for peer in peers_of(rule, 'from')), 'The probe pods need an ingress rule from the scout pod on TCP 8080'
for rule in ingress:
    for peer in peers_of(rule, 'from'):
        assert peer.get('podSelector') == {'matchLabels': {'app': 'scout'}}, 'The probe pods may receive traffic from the scout pod only'
probe_ip = kubectl('-n', 'starfleet', 'get', 'pod', '-l', 'app=probe', '-o', 'jsonpath={.items[0].status.podIP}')
scout_ip = kubectl('-n', 'starfleet', 'get', 'pod', 'scout', '-o', 'jsonpath={.status.podIP}')
for address in (probe_ip, scout_ip):
    behavior_check({'args': ['kubectl', '-n', 'outpost', 'exec', 'drifter', '--', 'wget', '-q', '-T', '3', '-O-', 'http://' + address + ':8080/'], 'denied': True, 'failure_markers': ['timed out']})
