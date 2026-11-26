# Verify A Signed Checksum Manifest

The `relay-agent` binary is offered on three mirrors in `/var/lib/relay-release` on the control plane node `astro-ats-031-lab-050-01-02-control-plane`. Each folder `mirror-a`, `mirror-b` and `mirror-c` holds `relay-agent`, a `SHA256SUMS` manifest and `SHA256SUMS.sig`, an RSA signature over the SHA-256 digest of `SHA256SUMS` made with `openssl dgst -sha256 -sign`. The publisher's public key is `/var/lib/relay-release/publisher.pub`. Only one mirror has the release that the publisher signed. Record your findings in the ConfigMap `artifact-review` in namespace `starfleet-031-050-01-02`.

1. Set the key `mirror` to the letter (`a`, `b` or `c`) of a mirror whose `SHA256SUMS.sig` verifies over its `SHA256SUMS` with `publisher.pub`.
2. Of those, the mirror you name must also have a `relay-agent` that matches its `SHA256SUMS`.
3. Set the key `sha256` to the `relay-agent` digest listed in that mirror's authenticated `SHA256SUMS`.

Do not run `relay-agent` and do not change the staged files; the roles of the mirrors are chosen at random each time the lab starts.
