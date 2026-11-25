address=get('pod','metadata-simulator')['status']['podIP']
assert 'Directory listing' in kubectl('-n','outpost','exec','drifter','--','wget','-q','-T','3','-O-','http://'+address+':8080/'), 'Keep the protected target healthy'
behavior_check({'args':['kubectl','-n','starfleet','exec','shuttle','--','wget','-q','-T','3','-O-','http://'+address+':8080/'],'denied':True,'failure_markers':['timed out']})
