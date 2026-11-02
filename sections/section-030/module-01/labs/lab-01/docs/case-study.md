---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# Starting Environment

The lab includes a working Traefik Ingress controller and healthy application. The required route has not been created.

Create a TLS Ingress `probe` for class `traefik`, host `probe.local`, Prefix path `/` and backend Service `probe` port 80. Use the supplied TLS Secret `probe-tls` and websecure entrypoint. A client trusting the supplied certificate must receive version one for the matching server name and must reject a mismatched server name. Preserve the original application and Service.
