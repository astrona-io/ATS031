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

get('networkpolicy', 'shuttle-egress-to-probe', 'outpost')
egress_rules = rules_for('outpost', {'app': 'shuttle'}, 'Egress')
assert len(egress_rules) == 2, 'The shuttle pod needs exactly two egress rules'
assert has_dns_rule(egress_rules), 'DNS to CoreDNS on UDP and TCP port 53 is missing'
probe_rules = [rule for rule in egress_rules if any(peer == {'podSelector': {'matchLabels': {'app': 'probe'}}} for peer in peers_of(rule, 'to'))]
assert len(probe_rules) == 1 and port_set(probe_rules[0]) == {('TCP', '8080', None)}, 'The probe egress rule must allow only TCP 8080'
no_open_rules(egress_rules)
behavior_check({'args': ['kubectl', '-n', 'outpost', 'exec', 'shuttle', '--', 'wget', '-q', '-T', '3', '-O-', 'http://probe.starfleet/'], 'denied': True, 'failure_markers': ['timed out']})
behavior_check({'args': ['kubectl', '-n', 'dock', 'exec', 'shuttle', '--', 'wget', '-q', '-T', '3', '-O-', 'http://probe.outpost/'], 'denied': True, 'failure_markers': ['timed out']})
