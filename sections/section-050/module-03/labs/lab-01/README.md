# Verify Detached GPG Signatures With gpgv

Author notes for the graded lab `ats-031-lab-050-03-01`. The learner reads `question.md` and,
after the attempt, `solution.md`.

- `bootstrap/setup.sh` creates the namespace and runs `bootstrap/sign-documents.sh`
  in a throwaway `buildpack-deps:bookworm-curl` container with `--network none`
  on the host. That script creates a publisher key, signs a random set of
  documents, damages some of them and streams the result as a tar into
  `/var/lib/doc-review` on the control plane node. The node itself only has
  `gpgv`. The host pulls the builder image if it is missing.
- `testing/live.py` recomputes the truth from the live state on every run and
  compares it with what the learner recorded. Nothing in the lab stores an
  answer key.
- `solution/apply.sh` is the reference solution that `astrona test` applies.

Run `astrona validate .` and `astrona test . --accept-terms --headless` in this
folder. `testing/verify-start.sh` checks that every outcome fails on the
starting state; after the reference solution every outcome must pass.
