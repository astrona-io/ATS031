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

if wants('shuttle-egress'):
    egress = rules_for('outpost', {'app': 'shuttle'}, 'Egress')
    no_open_rules(egress)
    assert has_dns_rule(egress), 'The shuttle pod needs a DNS rule to CoreDNS on UDP and TCP port 53'
    probe_peer = {'namespaceSelector': {'matchLabels': {'kubernetes.io/metadata.name': 'starfleet'}}, 'podSelector': {'matchLabels': {'app': 'probe'}}}
    assert any(peer == probe_peer and port_set(rule) == {('TCP', '8080', None)} for rule in egress for peer in peers_of(rule, 'to')), 'The shuttle pod needs an egress rule to the probe pods in starfleet on TCP 8080 only'
    external = {'ipBlock': {'cidr': '203.0.113.0/24', 'except': ['203.0.113.99/32']}}
    assert any(peer == external and port_set(rule) == {('TCP', '443', None)} for rule in egress for peer in peers_of(rule, 'to')), 'The shuttle pod needs the external range rule on TCP 443 with the one excluded address'
if wants('scout-egress'):
    dock_egress = rules_for('dock', {'app': 'scout'}, 'Egress')
    no_open_rules(dock_egress)
    assert has_dns_rule(dock_egress), 'The scout pod needs a DNS rule to CoreDNS on UDP and TCP port 53'
    api_address = kubectl('get', 'endpointslice', '-l', 'kubernetes.io/service-name=kubernetes', '-o', 'jsonpath={.items[0].endpoints[0].addresses[0]}')
    api_port = kubectl('get', 'endpointslice', '-l', 'kubernetes.io/service-name=kubernetes', '-o', 'jsonpath={.items[0].ports[0].port}')
    assert any(peer.get('ipBlock', {}).get('cidr') == api_address + '/32' and (('TCP', api_port, None) in port_set(rule)) for rule in dock_egress for peer in peers_of(rule, 'to')), 'The scout pod needs an egress rule to the API server endpoint address and port'
if wants('traffic-enforced'):
    probe_ip = kubectl('-n', 'starfleet', 'get', 'pod', '-l', 'app=probe', '-o', 'jsonpath={.items[0].status.podIP}')
    telemetry_ip = kubectl('-n', 'dock', 'get', 'pod', 'telemetry', '-o', 'jsonpath={.status.podIP}')
    behavior_check({'args': ['kubectl', '-n', 'outpost', 'exec', 'drifter', '--', 'wget', '-q', '-T', '3', '-O-', 'http://' + probe_ip + ':8080/'], 'denied': True, 'failure_markers': ['timed out']})
    behavior_check({'args': ['kubectl', '-n', 'outpost', 'exec', 'shuttle', '--', 'wget', '-q', '-T', '3', '-O-', 'http://' + telemetry_ip + ':8080/'], 'denied': True, 'failure_markers': ['timed out']})
    script = 'import sys, urllib.request\ntry:\n    urllib.request.urlopen("http://' + probe_ip + ':8080/", timeout=3)\nexcept Exception as error:\n    print("timed out" if "timed out" in str(error) else str(error))\n    sys.exit(1)\n'
    behavior_check({'args': ['kubectl', '-n', 'dock', 'exec', 'scout', '--', 'python', '-c', script], 'denied': True, 'failure_markers': ['timed out']})
