# Require Digest-Pinned Images At Admission

Author notes for the graded lab `ats-031-lab-050-03-05`. The learner reads `question.md` and,
after the attempt, `solution.md`.

- `bootstrap/setup.sh` creates the namespaces `starfleet-031-050-03-05` and
  `outpost-031-050-03-05`. There is no node staging. `testing/live.py` checks
  the admission result with `kubectl create --dry-run=server`, so the grader
  tests the policy itself, whatever names the learner chose.
- `testing/live.py` recomputes the truth from the live state on every run and
  compares it with what the learner recorded. Nothing in the lab stores an
  answer key.
- `solution/apply.sh` is the reference solution that `astrona test` applies.

Run `astrona validate .` and `astrona test . --accept-terms --headless` in this
folder. `testing/verify-start.sh` checks that every outcome fails on the
starting state; after the reference solution every outcome must pass.
