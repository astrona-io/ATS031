# Repair A Policy That Names The Service Port And Add A Port Range

In namespace `starfleet-031-010-03-06`, pod `visitor` cannot reach the Service `kiosk` on port 80, which sends requests to the container port `http` (TCP 8080) of the two `kiosk` replicas (label `app: kiosk`). The `kiosk` pods also serve metrics on TCP ports 9100 to 9102 for pod `collector`. The NetworkPolicies `default-deny-ingress` and `kiosk-ingress` exist.

Repair the NetworkPolicy `kiosk-ingress` so that:

1. pod `visitor` reaches the Service `kiosk` on port 80 and every `kiosk` replica on TCP 8080;
2. a rule allows TCP ports 9100 to 9102 with one port item that uses `endPort`, and the policy opens no port other than 8080 and that range;
3. pod `collector` reaches TCP 9100 and 9102 on every `kiosk` replica, while `visitor` cannot reach the metrics ports and `collector` cannot reach TCP 8080.

Keep `default-deny-ingress` as it is, and add no other NetworkPolicy.
