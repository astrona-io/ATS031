# Use Network security policies to restrict cluster level access

Picture a pod that holds a database password. Any other pod in the cluster can open a connection to it, even a pod in a different namespace that has nothing to do with the database. This is how Kubernetes works out of the box: every pod can talk to every other pod.

A NetworkPolicy is the Kubernetes object that changes this. It selects a group of pods and lists the connections those pods may receive (ingress) or make (egress). The network plugin of the cluster, the Container Network Interface (CNI) plugin, reads the policy and drops every other connection.

NetworkPolicy looks simple, but it is easy to get wrong. A pod stays open until a policy selects it. Several policies add up, so one loose rule can open a door that another rule closed. In this section, you learn how these rules work and how to prove that they do what you meant.

## What you will learn

The section moves from a single policy to a whole cluster:

- **Restrict Pod Traffic With NetworkPolicy.** How a policy isolates a pod, how to allow one caller in, how to let a pod reach DNS and the services it needs, and how to find out why a connection fails.
- **Build Default-Deny Baselines For Namespaces.** Close a namespace first, then open only what it needs. You also see what breaks when you deny egress, and how to roll a baseline out to many namespaces.
- **Select Peers And Ports Precisely.** Choose callers by namespace and by pod label, and learn why one peer entry with two selectors means something different from two entries. You also allow IP ranges with exceptions, and limit traffic to ports and port ranges.
- **Policy For Real Cluster Traffic And Troubleshooting.** Keep DNS, the API server and health probes working under a strict policy, deal with `hostNetwork` pods, and audit a policy set with a test matrix.

## How this section works

Each module has its own playground: a private `kind` cluster that runs Kubernetes v1.35. Start it from the first page of the module and keep it running while you read, because every page has commands to try.

When a page teaches a skill you can be graded on, a lab comes right after it. A lab gives you a short task in a fresh cluster and checks your result. Each module ends with a summary and a short knowledge check.

## By the end of this section

You will be able to:

- explain which pods a policy isolates, in which direction, and how several policies combine;
- write an ingress policy that lets one labelled pod in and keeps all others out, including pods in other namespaces;
- write an egress policy that allows DNS and one dependency, and blocks everything else;
- explain why `namespaceSelector` and `podSelector` in one peer entry differ from two separate peer entries;
- test a policy with one request that must pass and one that must fail, and tell a timeout from a refused connection.
