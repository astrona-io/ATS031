# Apply One Baseline To Labelled Namespaces

The teams in `cargo-031-010-02-05` (pod `loader`) and `fuel-031-010-02-05` (pod `pump`) have agreed to a default-deny baseline. The team in `galley-031-010-02-05` (pod `cook`) has not, and its namespace must stay open for now.

1. Add the label `netpol=restricted` to the namespaces `cargo-031-010-02-05` and `fuel-031-010-02-05`, and not to `galley-031-010-02-05`.
2. Write one manifest for a NetworkPolicy named `default-deny-all` that selects every pod for both ingress and egress with no rules, leave its `namespace` field out, and apply that file to every namespace with the label `netpol=restricted`.
3. Make the baseline take effect: `cook` times out to `loader` and `pump` on TCP port 8080, `pump` can no longer resolve names, and `cook` still resolves names through CoreDNS.

Do not create any NetworkPolicy in `galley-031-010-02-05`.
