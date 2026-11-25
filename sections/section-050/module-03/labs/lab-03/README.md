# Verify And Create Blob Signatures With cosign

Author notes for the graded lab `ats-031-lab-050-03-03`. The learner reads `question.md` and,
after the attempt, `solution.md`.

- `bootstrap/setup.sh` creates the namespace, copies `/ko-app/cosign` from the
  `ghcr.io/sigstore/cosign/cosign:v2.4.1` image to `/usr/local/bin/cosign` on
  the control plane node, and runs `bootstrap/stage-node.sh` there. The staging
  script signs six build records with a new key, damages two or three of them
  at random (changed content, other key or missing signature), deletes the
  private keys and creates the approval file. The node needs no network:
  every cosign call uses `--tlog-upload=false` or `--insecure-ignore-tlog=true`.
- `testing/live.py` recomputes the truth from the live state on every run and
  compares it with what the learner recorded. Nothing in the lab stores an
  answer key.
- `solution/apply.sh` is the reference solution that `astrona test` applies.

Run `astrona validate .` and `astrona test . --accept-terms --headless` in this
folder. `testing/verify-start.sh` checks that every outcome fails on the
starting state; after the reference solution every outcome must pass.
