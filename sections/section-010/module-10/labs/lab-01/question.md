# Allow One Peer And Deny Another

In namespace `starfleet-031-010-01-01`, only pod `tender` may reach the `hub` pods (label `app: hub`, TCP port 8080).

Create a NetworkPolicy named `hub-from-tender` in `starfleet-031-010-01-01` that:

1. selects the `hub` pods and covers ingress only;
2. allows TCP port 8080 only from pods labelled `app: tender` in the same namespace, so `tender` reaches the Service `hub` and both replicas;
3. blocks pod `idler` and pod `stranger` (namespace `outpost-031-010-01-01`) from `hub`.

Do not create any other NetworkPolicy in either namespace. `idler` and `stranger` must still reach pod `mirror`.
