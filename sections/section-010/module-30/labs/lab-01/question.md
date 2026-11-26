# Allow One Pod From Another Namespace

In namespace `starfleet-031-010-03-01`, only pod `courier` in namespace `outpost-031-010-03-01` may reach pod `registry` (label `app: registry`, TCP port 8080). Pods named `courier` with the label `app: courier` also run in `starfleet-031-010-03-01` and `dock-031-010-03-01`.

Create a NetworkPolicy named `registry-from-outpost-courier` in `starfleet-031-010-03-01` that:

1. selects the `registry` pod for ingress and allows TCP port 8080 from one peer entry that has both a `namespaceSelector` for `outpost-031-010-03-01` and a `podSelector` for `app: courier`;
2. lets pod `courier` in `outpost-031-010-03-01` reach `registry` on TCP 8080;
3. blocks pod `idler` in `outpost-031-010-03-01` and the `courier` pods in `starfleet-031-010-03-01` and `dock-031-010-03-01` from `registry`.

Do not create any other NetworkPolicy, in `starfleet-031-010-03-01` or in any other namespace.
