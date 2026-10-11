---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Summary

Ingress resources declare host and path routing to Service backends, while a suitable controller implements the traffic path. Class selection and reachable entry infrastructure are independent requirements.

Backend references use the Service port contract. Path matching does not universally rewrite the application path, and external encrypted transport does not automatically encrypt the controller-to-backend connection.
