# Curriculum Coverage

Exam: Certified Kubernetes Security Specialist (CKS). Domain: Cluster Setup (15%).

The [official objectives](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/) were checked on 2026-10-11. Teaching structure is independently authored and does not add official requirements.

| Section | Official objective | Modules |
| --- | --- | --- |
| 010 | Use Network security policies to restrict cluster level access | 4 |
| 020 | Use CIS benchmark to review the security configuration of Kubernetes components (etcd, kubelet, kubedns, kubeapi) | 5 |
| 030 | Properly set up Ingress with TLS | 4 |
| 040 | Protect node metadata and endpoints | 3 |
| 050 | Verify platform binaries before deploying | 3 |

| Section / module | Module | Teaching files |
| --- | --- | --- |
| 010 / 01 | Restrict Pod Traffic With NetworkPolicy | How NetworkPolicy Isolation Works; Allow One Peer With An Ingress Policy; Restrict Egress And Allow DNS; Default Deny And Troubleshooting Policies |
| 010 / 02 | Build Default-Deny Baselines For Namespaces | Why A Baseline Comes First; Deny All Ingress; Deny All Egress And Its Side Effects; Combine Baselines With Allow Rules; Baselines Across Many Namespaces |
| 010 / 03 | Select Peers And Ports Precisely | Selectors Recap And The Namespace Name Label; Cross-Namespace Ingress; One Entry Versus Two Entries; ipBlock And Except; Ports, Protocols And endPort; Policies On Services And Replicas |
| 010 / 04 | Policy For Real Cluster Traffic And Troubleshooting | DNS And CoreDNS Egress; Egress To The API Server And Other Dependencies; Probes, hostNetwork And Node Traffic; Test Matrix For A Policy Set; Audit And Troubleshoot Policies |
| 020 / 01 | Review Kubernetes Components With The CIS Benchmark | The Benchmark And Where The Settings Live; Read A Check: kube-bench And The Manual Audit; Review The Kubelet: Effective Configuration And File Permissions; Correct A Finding Safely And Record It |
| 020 / 02 | Run kube-bench And Read Its Output | What kube-bench Does Under The Hood; Run kube-bench On A kubeadm Node; Targets, Benchmarks And Versions; Read A Result; Select Checks And Export Results; Manual Checks And False Findings |
| 020 / 03 | Harden The API Server And Control Plane Components | Static Pods And Safe Editing; Authentication And Authorization Flags; Admission Plugins; Audit Logging; Profiling, TLS And Service Account Flags; Controller Manager, Scheduler And File Permissions |
| 020 / 04 | Review etcd Security Configuration | What Lives In etcd And Who Talks To It; Client And Peer TLS Flags; Data Directory Ownership And Permissions; Query etcd With etcdctl; Encryption At Rest Check |
| 020 / 05 | Harden The kubelet And CoreDNS, Then Remediate End To End | Kubelet Configuration Sources; Kubelet Authentication And Authorization; Read-Only Port, Ports And TLS Settings; Other Kubelet Checks; Review CoreDNS (kube-dns); Remediate Findings End To End |
| 030 / 01 | Set Up Ingress With TLS | Ingress Routing: Controller, Class, Host And Path; Certificates And The TLS Secret; Configure An Ingress With TLS And Verify It; Several Hosts, Server Name Selection And Troubleshooting |
| 030 / 02 | Run Traefik On kind | Ingress Controller Architecture With Traefik; Read The Traefik Installation On kind; First Ingress And Host Header Testing; Path Types And Priority; Several Services And A Default Backend; Inspect The Running Controller |
| 030 / 03 | Build TLS With openssl For Traefik | Certificate Fundamentals Needed For The Exam; Self-Signed Certificate With openssl; Sign A Server Certificate With Your Own CA; Create The TLS Secret; Configure spec.tls And Verify; HTTPS Redirect, HSTS And The Default Certificate |
| 030 / 04 | Harden And Troubleshoot Traefik TLS | TLS Versions, Ciphers And Server Names; Mutual TLS With Client Certificates; Shrink The Controller Attack Surface; Rotate And Replace Certificates; Troubleshoot TLS Ingress Failures |
| 040 / 01 | Protect Node Metadata And Management Endpoints | Endpoints That Carry Authority; Network Paths To A Metadata-Style Endpoint; Restrict The Pod And Verify The Boundary |
| 040 / 02 | Block The Cloud Metadata Endpoint | What The Metadata Service Hands Out; The Playground Metadata Server; Block With An ipBlock Except Rule; Default Deny Plus A Selective Allow; Policy Pitfalls For The Metadata Address; Verify Coverage Across Namespaces |
| 040 / 03 | Protect Node Endpoints And The Runtime | The Kubelet API From A Pod; Restrict Reachability To Node Ports; Node Identity And NodeRestriction; Runtime Socket And hostPath Exposure; hostNetwork And Privileged Pods Bypass Policy; Controls Outside The Cluster |
| 050 / 01 | Verify Platform Binaries Before Deploying | Integrity, Authenticity And The Exact Artifact; Digests At Work And The Limits Of A Checksum; Verify A Signed Manifest And Record The Result; Keep The Binding Through Delivery, And Identity-Based Signatures |
| 050 / 02 | Verify Kubernetes Release Binaries Hands-On | Kubernetes Release Artifacts; sha256sum And The Check Format; Detect A Tampered Or Wrong Binary; Read The Version Of A Binary; Verify What Runs On A Node |
| 050 / 03 | Verify Packages, Images And Signatures | GPG Signed Repositories; Package Verification On A Node; cosign With A Local Key Pair; Keyless Verification And Release Signatures; Image Digests And Pinning; SBOMs And Admission-Time Verification |

AUTHORING.yaml records measurable goals and adaptation sources. Every objective retains its section ID. Technical readings carry no draft marker; the ATP registration stays draft until publication is approved. Question banks are separate from the reading manifest and follow their declared summaries. A playground and graded labs accompany each module. Live results are recorded below.

## Hands-On Coverage

This course has 19 ungraded module playgrounds and 87 independent labs. Each lab's task and solution are registered immediately after the reading it practises. CI ran `astrona test` on every lab and playground on 2026-11-21 (amd64, kind and qemu, run 44896016231 on `main`): all 87 labs and 19 playgrounds passed.

| Module | Labs in teaching order |
| --- | --- |
| 010/01 | Allow One Peer And Deny Another |
| 010/01 | Allow DNS And One Application Dependency |
| 020/01 | Disable API Server Profiling In A Private Node |
| 030/01 | Verify TLS Termination And Server Identity |
| 040/01 | Block A Simulated Metadata Endpoint |
| 050/01 | Verify Signed Artifact Checksums |
