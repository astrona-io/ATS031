# Node Identity And NodeRestriction

A kubelet talks to the API server with its own credential. If an attacker steals that credential, the damage depends on what a node is allowed to do. Kubernetes limits a node with two features: the node authorizer and the `NodeRestriction` admission plugin.

On this page, you learn what each feature does. You confirm that both are switched on in the playground. Then you test what a node identity is allowed to read.

## Who a node is

A kubelet authenticates with a client certificate. The certificate names the user `system:node:<node name>` and puts that user in the group `system:nodes`. The API server then decides what this user may do.

Ordinary RBAC rules for nodes would have to cover every pod on every node, so Kubernetes uses a special authorizer instead. The node authorizer lets a kubelet read the objects that belong to pods scheduled on its own node. These are the pods themselves, and the Secrets, ConfigMaps, PersistentVolumeClaims and PersistentVolumes that those pods reference. The node authorizer refuses the same requests for objects that belong to other nodes. So a kubelet cannot list all Secrets in the cluster, even though it needs Secrets to start pods.

Authorization alone is not enough for writes. A kubelet must be able to update its own Node object and the status of its own pods. The `NodeRestriction` admission plugin checks these writes. An admission plugin is a step in the API server that checks a request after authorization and can reject it. `NodeRestriction` allows a kubelet to change only its own Node object and only the pods bound to its node. It refuses changes to other nodes.

`NodeRestriction` also restricts labels, and the rules are:

- A kubelet may not set or change labels with the prefix `node-restriction.kubernetes.io/`.
- A kubelet may not set most labels with the prefixes `kubernetes.io` and `k8s.io`.
- A short list of well-known labels stays allowed, such as the host name, the operating system and the architecture.

The label rule matters because schedulers and policies trust labels. Suppose a compromised node could label itself with `node-restriction.kubernetes.io/dedicated=payments`. Then the scheduler would place workloads that select that label onto the node, and the node would collect their Secrets.

![Diagram: a node credential of the form system:node: plus the node name may read its own pods and their Secrets and may write its own Node object; the node authorizer refuses Secrets of other nodes and NodeRestriction refuses writes to other nodes and to protected labels](images/node-credential-limits.svg)

The drawing shows the two limits on a node credential. The node authorizer limits reads, and `NodeRestriction` limits writes.

## Confirm both are enabled

The two features only help if they are switched on, so check that first. Both are set as flags on the API server. A cluster built with kubeadm, which is what `kind` builds, runs the API server as a static pod. A static pod is a pod that the kubelet starts from a file on the node, so you can read its command line through the API. This command prints each flag on its own line and keeps the two that matter:

<!-- astrona:playground:renew -->

```sh
kubectl -n kube-system get pod -l component=kube-apiserver -o jsonpath='{.items[0].spec.containers[0].command}' | tr ',' '\n' | grep -E 'authorization-mode|enable-admission-plugins'
```

The first line should show an authorization mode list that contains `Node` and `RBAC`. The second should show a plugin list that contains `NodeRestriction`. Each missing value is a finding:

- If `Node` is missing, kubelets would fall back on other authorizers.
- If `NodeRestriction` is missing, a node credential could change objects of other nodes.

## Test what a node may read

With both features on, you can test what a node identity may do. You do not need the node's credential for this. The `--as` and `--as-group` options make `kubectl` impersonate the node, and the API server answers as if the node asked. Your own account needs the permission to impersonate, and the playground administrator account has it.

Store the worker name and ask three questions:

```sh
WORKER=$(kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o jsonpath='{.items[0].metadata.name}')
kubectl auth can-i list secrets -A --as="system:node:$WORKER" --as-group=system:nodes
kubectl auth can-i delete nodes --as="system:node:$WORKER" --as-group=system:nodes
kubectl auth can-i get nodes --as="system:node:$WORKER" --as-group=system:nodes
```

The first two answers should be `no`: the node cannot list all Secrets, and it cannot delete nodes. The third should be `yes`, because a kubelet reads Node objects. The answers depend on how the chain of authorizers is set up. So treat a result that differs as a finding to investigate, not as a mistake in the command.

The label rule is harder to test. It needs the node's own credential, which lives in a file on the node, and the playground does not make you use it. Remember the rule instead: a node credential can change only its own Node object, and labels with the protected prefix are outside its reach.

You now know how the cluster limits a stolen node credential. The limits are strong, but they only cover the credential. The open question is whether a pod can take control of the node by another route, without any credential.

## Common pitfalls

> [!WARNING]
> - **Assuming a node credential is harmless.** It can read the Secrets of the pods on that node, so a pod with sensitive Secrets makes that node a more valuable target.
> - **Removing `Node` from the authorizer list or `NodeRestriction` from the plugins.** The cluster needs both.
> - **Trusting a node label for isolation.** Use the protected `node-restriction.kubernetes.io/` prefix for labels that a policy relies on.
> - **Reading the impersonation answer as a full test.** It shows the decision of the authorizer, not the behaviour of the admission plugin.
