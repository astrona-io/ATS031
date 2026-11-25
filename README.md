<p align="center">
  <a href="https://astrona.io/courses/certified-kubernetes-security-specialist">
    <img src="https://astrona.io/courses/certified-kubernetes-security-specialist/domains/ATS031.svg" alt="ATS031: Cluster Setup, part of the Certified Kubernetes Security Specialist course on Astrona" width="100%">
  </a>
</p>

# Certified Kubernetes Security Specialist (CKS) - Cluster Setup (ATS031)

Learn to lock down a Kubernetes cluster before anything runs on it. This course covers the Cluster Setup domain of the Certified Kubernetes Security Specialist (CKS) exam, which is 15% of the score.

You read how each control works, try it in your own playground, and then prove it in a graded lab. Take the course on [Astrona](https://astrona.io/courses/certified-kubernetes-security-specialist).

## What you will learn

**Network policies.** Restrict pod traffic, build default-deny baselines, select peers and ports precisely, and troubleshoot a policy set.

- Restrict Pod Traffic With NetworkPolicy
- Build Default-Deny Baselines For Namespaces
- Select Peers And Ports Precisely
- Policy For Real Cluster Traffic And Troubleshooting

**CIS benchmark.** Review the API server, etcd, kubelet and CoreDNS with kube-bench, and fix what it finds.

- Review Kubernetes Components With The CIS Benchmark
- Run kube-bench And Read Its Output
- Harden The API Server And Control Plane Components
- Review etcd Security Configuration
- Harden The kubelet And CoreDNS, Then Remediate End To End

**Ingress with TLS.** Serve applications over HTTPS with Traefik and your own certificates.

- Set Up Ingress With TLS
- Run Traefik On kind
- Build TLS With openssl For Traefik
- Harden And Troubleshoot Traefik TLS

**Node metadata and endpoints.** Keep pods away from the metadata service, the kubelet and the container runtime.

- Protect Node Metadata And Management Endpoints
- Block The Cloud Metadata Endpoint
- Protect Node Endpoints And The Runtime

**Platform binaries.** Check binaries, packages and images before you trust them.

- Verify Platform Binaries Before Deploying
- Verify Kubernetes Release Binaries Hands-On
- Verify Packages, Images And Signatures

## How the course works

- **Reading pages** explain one idea at a time, with real commands and output.
- **Playgrounds** are private, ungraded environments for following along. Most run on kind (Kubernetes in Docker); the CIS benchmark modules use a QEMU virtual machine.
- **Labs** give you an exam-style task in a fresh environment and grade the result.
- **Knowledge checks** close each module with a short quiz.

You start playgrounds and labs with the `astrona` CLI, and work in a browser workspace with a terminal ready to use.

## Contributing

Found a mistake or want to improve something? See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Created by Astrona.io. Course content is licensed under [CC BY-NC-SA 4.0](LICENSE-CONTENT), and code under [AGPL v3](LICENSE). See [NOTICE](NOTICE) for details.
