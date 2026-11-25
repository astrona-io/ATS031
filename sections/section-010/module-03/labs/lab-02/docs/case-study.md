---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

The namespace `dock-031-010-03-02` runs the pods `assay` and `sampler`. The namespace `starfleet-031-010-03-02` runs the pods `sampler` and `idler`, and the namespace `outpost-031-010-03-02` runs one more pod named `sampler`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. Each namespace has the automatic label `kubernetes.io/metadata.name: <namespace name>`.

The NetworkPolicy `assay-from-starfleet` in `dock-031-010-03-02` selects the `assay` pod. Its one ingress rule lists two peer entries: a `namespaceSelector` for `starfleet-031-010-03-02`, and a separate `podSelector` for `app: sampler`.
