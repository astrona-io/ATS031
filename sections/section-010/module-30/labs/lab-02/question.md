# Repair A Two-Entry Peer Rule

In namespace `dock-031-010-03-02`, the NetworkPolicy `assay-from-starfleet` should let only pod `sampler` in namespace `starfleet-031-010-03-02` reach pod `assay` (label `app: assay`, TCP port 8080). Today pod `idler` in `starfleet-031-010-03-02` and pod `sampler` in `dock-031-010-03-02` get in too.

Repair the NetworkPolicy `assay-from-starfleet` in `dock-031-010-03-02` so that:

1. its ingress rule allows TCP port 8080 only through peer entries that each have both a `namespaceSelector` for `starfleet-031-010-03-02` and a `podSelector` for `app: sampler`;
2. pod `sampler` in `starfleet-031-010-03-02` reaches `assay` on TCP 8080, and pod `idler` in `starfleet-031-010-03-02` is blocked;
3. the `sampler` pods in `dock-031-010-03-02` and `outpost-031-010-03-02` are blocked from `assay`.

Keep the policy name. Do not add any other NetworkPolicy, in `dock-031-010-03-02` or in any other namespace.
