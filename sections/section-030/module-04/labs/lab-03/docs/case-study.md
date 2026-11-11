# Case study



Traefik serves `probe.example.test` using `probe-tls` in `rotation-training`. A replacement certificate and key are staged in `probe-next`, signed by the existing training CA. `probe-old` preserves the previous pair.

Allow about 10 minutes for the tasks.
