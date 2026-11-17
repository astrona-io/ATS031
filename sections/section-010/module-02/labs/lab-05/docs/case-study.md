---
exam_objectives:
- Use Network security policies to restrict cluster level access
---
# Starting Environment

Three namespaces exist: `cargo-031-010-02-05` runs the pod `loader`, `fuel-031-010-02-05` runs the pod `pump` and `galley-031-010-02-05` runs the pod `cook`. Each pod has the label `app: <pod name>`, serves HTTP on TCP port 8080 and contains a small test client, `/app/client.py`. No NetworkPolicy exists and no namespace carries a `netpol` label.
