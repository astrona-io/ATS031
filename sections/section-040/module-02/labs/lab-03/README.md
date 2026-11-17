# Repair Metadata Policies That Do Not Block

Three namespaces each have a NetworkPolicy called `metadata-guard` that was meant to block the cloud metadata address. None of them does its job: two leave the address open and one breaks every Service request. The learner finds each mistake and repairs it.

Run `astrona test` on this folder: `testing/verify-start.sh` checks that every outcome fails on the starting state, then the reference solution is applied and every outcome must pass.
