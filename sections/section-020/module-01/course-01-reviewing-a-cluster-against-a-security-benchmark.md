---
draft: true
exam_objectives:
- Use CIS benchmark to review the security configuration of Kubernetes components
  (etcd, kubelet, kubedns, kubeapi)
---
# Reviewing A Cluster Against A Security Benchmark

A security benchmark turns broad goals into concrete recommendations that can be assessed. The CIS Kubernetes Benchmark is a versioned collection of such recommendations. It is useful for examining control-plane and worker configuration, but it is not a universal script that can safely rewrite every cluster. An assessment starts by identifying the Kubernetes release, benchmark edition, deployment model and ownership of each component.

## Match The Assessment To The Deployment

An administrator of a self-managed control plane may inspect static Pod manifests, component arguments and host file permissions. A user of a managed service may not have access to those resources. The latter needs provider documentation or assurance evidence for provider-owned controls, together with direct assessment of customer-owned settings. Marking an inaccessible control as passed would confuse unavailable evidence with demonstrated protection.

Benchmarks can distinguish different recommendation levels and automated or manual assessment procedures. More restrictive recommendations can require operational tradeoffs. Select a profile appropriate to the system's risk and supported architecture. Record the selected edition so another reviewer can interpret the result and reproduce the reasoning rather than guess which defaults the report assumed.

## Follow Effective Configuration

A finding about the API server might concern anonymous authentication, authorization or admission. A kubelet finding might concern authentication, authorization or an exposed endpoint. Etcd assessment includes authenticated transport and access to data or credentials. File ownership and permissions protect component configuration from modification. DNS security also involves the supported DNS implementation, service permissions and exposure rather than treating a historical component name as a current architecture requirement.

The relevant setting is the value the running component actually uses. A secure value in an unused configuration file does not protect a component launched with different arguments. Conversely, a check that expects an older flag may misinterpret a newer structured configuration. Trace startup definitions, active configuration and documented defaults before deciding whether a recommendation is satisfied.

## Interpret Findings Before Remediation

Suppose a report identifies overly permissive access to a kubelet configuration file. First establish the actual file loaded, owner, allowed readers and writers, and the host identities that need access. A correction should remove unnecessary authority without preventing the kubelet from reading its configuration. A permission change that stops the service is not an acceptable security outcome merely because one check becomes green.

Some checks require human review, such as whether granted API permissions are justified. An automated assessment can enumerate bindings but cannot infer every team's business responsibility. Distinguish a tool's observation from the security decision made from it. Tools such as kube-bench evaluate supported benchmark checks; their report still needs interpretation and does not perform every application security assessment.

## Preserve Evidence And Exceptions

Record the finding, observed effective state, intended correction, responsible owner and verification evidence. Where a recommendation cannot be adopted, explain the reason, remaining risk and compensating controls. Exceptions should have review ownership and a lifecycle, especially after upgrades that change available settings.

Reassessment should confirm both the security setting and required component behavior. Authentication changes need evidence that legitimate callers can still authenticate; authorization changes need evidence of the intended permitted and denied operations. A passing benchmark result does not establish secure application code, complete network isolation or trustworthy build artifacts. Those require their own controls and evidence.

## Common pitfalls

> [!WARNING]
> A benchmark pass is scoped evidence. An inaccessible setting, an unused configuration file and an unsupported check must not be reported as verified runtime protection.
