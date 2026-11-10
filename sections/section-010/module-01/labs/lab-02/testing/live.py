if wants('shuttle-egress-enforced'):
    blocked=get('pod','blocked-server')
    address=blocked['status']['podIP']
    # Establish that the denied target has a listener using an unrestricted client.
    assert 'Directory listing' in kubectl('-n','outpost-031-010-01-02','exec','drifter','--','wget','-q','-T','3','-O-','http://'+address+':8080/'), 'Denied target must have a working listener'
    behavior_check({'args':['kubectl','-n','starfleet-031-010-01-02','exec','shuttle','--','wget','-q','-T','3','-O-','http://'+address+':8080/'],'denied':True,'failure_markers':['timed out']})
