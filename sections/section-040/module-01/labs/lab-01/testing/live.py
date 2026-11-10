if wants('metadata-simulator'):
    address=get('pod','metadata-simulator')['status']['podIP']
    assert 'Directory listing' in kubectl('-n','outpost-031-040-01-01','exec','drifter','--','wget','-q','-T','3','-O-','http://'+address+':8080/'), 'Keep the protected target healthy'
if wants('shuttle-isolation'):
    address=get('pod','metadata-simulator')['status']['podIP']
    behavior_check({'args':['kubectl','-n','starfleet-031-040-01-01','exec','shuttle','--','wget','-q','-T','3','-O-','http://'+address+':8080/'],'denied':True,'failure_markers':['timed out']})
