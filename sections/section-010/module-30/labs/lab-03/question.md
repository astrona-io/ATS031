# Admit A Group Of Namespaces By Label

In namespace `starfleet-031-010-03-03`, pod `archive` (label `app: archive`, TCP port 8080) must accept requests from every namespace in the science division. The namespaces `survey-031-010-03-03`, `salvage-031-010-03-03` and `outpost-031-010-03-03` each run a pod named `mapper`.

1. Add the label `division=science` to the namespaces `survey-031-010-03-03` and `salvage-031-010-03-03`, and not to `outpost-031-010-03-03`.
2. Create a NetworkPolicy named `archive-from-science` in `starfleet-031-010-03-03` that selects the `archive` pod for ingress and allows TCP port 8080 from every pod in a namespace labelled `division=science`. Select the namespaces by that label, not by their names.
3. The `mapper` pods in `survey-031-010-03-03` and `salvage-031-010-03-03` reach `archive` on TCP 8080, and the `mapper` pod in `outpost-031-010-03-03` is blocked.

Do not label `outpost-031-010-03-03` and do not restrict the senders with a `podSelector`.
