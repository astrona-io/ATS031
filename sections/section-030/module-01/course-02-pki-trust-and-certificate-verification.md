---
draft: true
exam_objectives:
- Properly set up Ingress with TLS
---
# PKI Trust And Certificate Verification

Public key infrastructure (PKI) organizes certificates, keys and trusted authorities used to establish identities. A certificate associates an identity with a public key under an issuer's signature. The corresponding private key proves possession and must remain protected. This is an identity system, not merely a file format needed to silence connection errors.

## Keys And Certificate Authorities

A public key can be shared for relevant cryptographic operations. A private key must be restricted to the intended holder. Copying the private key gives another actor the capability to act under that key's identity where it is accepted. File names and certificate labels do not prevent that misuse.

A certificate authority (CA) signs certificates within a defined trust arrangement. A client trusts an issuer or root through configured trust material. The trust decision therefore depends on which authorities are accepted and what identities they are permitted to issue, not simply on whether a certificate contains a signature.

An intermediate authority can link a leaf certificate to a trusted root. Verification checks the relevant chain, validity and intended use. Expired or unsuitable certificates should lead to investigation of issuance and rotation rather than automatic disabling of checks.

## Identifying The Intended Peer

For a server connection, the client should verify that the certificate's accepted identity matches the endpoint it intends to reach. Subject alternative names can identify allowed hostnames or other identity forms according to the protocol and verifier. A certificate trusted for one name is not automatically trusted for every server address.

Transport Layer Security (TLS) establishes a protected channel with peer verification under the configured contract. Mutual TLS additionally authenticates the client through its certificate. Authentication does not grant every operation; the server still needs authorization based on the verified identity and requested action.

A workload certificate can represent a service rather than a human user. Application user identity can require a separate credential. State which identity the certificate proves and which policy uses it. A valid service identity should not silently become permission to read every user's data.

## Cluster And Workload Boundaries

Kubernetes components can use certificates for application programming interface (API) and peer connections. The API server's serving certificate, a node's client identity and datastore peer trust have different jobs. Giving all parties the same powerful credential weakens both containment and attribution.

A service mesh can automate workload certificate issuance and renewal. The issuer, identity mapping and control components become part of the trusted system. A mistaken mapping can issue a valid certificate for the wrong authority, so automation does not eliminate the need to protect issuance rules.

## Rotation And Lifetime

Certificates have validity intervals, and private keys can need replacement. Rotation should ensure legitimate peers trust the new material before the previous one expires or is withdrawn. Trust bundles can require a controlled overlap during planned issuer changes. A process may need reload or restart to adopt new files depending on its implementation.

Shorter lifetimes reduce some continued usefulness after exposure, but they also require reliable renewal. An outage in issuance can become an application availability problem when existing identities expire. Monitor renewal and verify the effective identity actually used by consumers.

Revocation and rejection behavior depend on the protocol and implementation. Do not assume that deleting a certificate file instantly makes every already-issued credential invalid everywhere. Compromise response needs the actual trust and credential-validation mechanisms, plus appropriate key and authority replacement.

## A Verification Failure Scenario

A client rejects a server because its name does not match. The protected response is to inspect the target, certificate names and trusted deployment configuration. Disabling verification accepts a weaker contract and can permit impersonation. A valid chain to the wrong name is not enough to establish the intended peer.

A complete PKI explanation identifies holder, issuer, accepted identity, permitted use and lifecycle. These details connect encrypted communication to trusted authority while preserving the distinction between authenticated identity and allowed application behavior.

## Common pitfalls

> [!WARNING]
> A trusted signature does not make a certificate valid for every name or use. Protect private keys, verify peer identity and understand actual rotation and revocation behavior before claiming compromised authority is removed.
