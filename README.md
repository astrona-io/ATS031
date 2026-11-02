# Cluster Setup (ATS031)

Certified Kubernetes Security Specialist (CKS): Cluster Setup, worth 15% of the official curriculum. This course belongs to ATP007.

Developed reading explains mechanisms, responsible components, examples and limits. Every section has an introduction and every module closes with a summary. Reusable YAML checks contain 5–15 questions per bank. Each module is a short landing page followed by deep-dive parts that carry the hands-on steps, a closing summary and a ten-question knowledge check. Technical content remains draft. Private playgrounds and draft graded labs are included.

## Course Outline

| Section / module | Module | Teaching files |
| --- | --- | --- |
| 010 / 01 | Restrict Pod Traffic With NetworkPolicy | How NetworkPolicy Isolation Works; Allow One Peer With An Ingress Policy; Restrict Egress And Allow DNS; Default Deny And Troubleshooting Policies |
| 020 / 01 | Review Kubernetes Components With The CIS Benchmark | The Benchmark And Where The Settings Live; Read A Check: kube-bench And The Manual Audit; Review The Kubelet: Effective Configuration And File Permissions; Correct A Finding Safely And Record It |
| 030 / 01 | Set Up Ingress With TLS | Ingress Routing: Controller, Class, Host And Path; Certificates And The TLS Secret; Configure An Ingress With TLS And Verify It; Several Hosts, Server Name Selection And Troubleshooting |
| 040 / 01 | Protect Node Metadata And Management Endpoints | Endpoints That Carry Authority; Network Paths To A Metadata-Style Endpoint; Restrict The Pod And Verify The Boundary |
| 050 / 01 | Verify Platform Binaries Before Deploying | Integrity, Authenticity And The Exact Artifact; Digests At Work And The Limits Of A Checksum; Verify A Signed Manifest And Record The Result; Keep The Binding Through Delivery, And Identity-Based Signatures |

## Author Review

See [curriculum coverage](CURRICULUM.md), [primary sources](SOURCES.md), [question-bank documentation](ASSESSMENTS.md) and [contribution instructions](CONTRIBUTING.md). No runtime execution is claimed.

## Hands-On Coverage

This course has 5 ungraded module playgrounds and 6 draft independent labs. Tasks and solutions are registered around each lab immediately after its teaching reading. Static configuration, shell/Python/YAML, parser, lifecycle and offline grader checks pass. Live execution remains pending because the session cannot access Podman; installed CLI configuration validation is separately blocked by its maintenance lock.

| Module | Labs in teaching order |
| --- | --- |
| 010/01 | Allow One Peer And Deny Another |
| 010/01 | Allow DNS And One Application Dependency |
| 020/01 | Disable API Server Profiling In A Private Node |
| 030/01 | Verify TLS Termination And Server Identity |
| 040/01 | Block A Simulated Metadata Endpoint |
| 050/01 | Verify Signed Artifact Checksums |
