# Verify Downloads With sha256sum --check

Author notes for the graded lab `ats-031-lab-050-02-02`. The learner reads `question.md` and,
after the attempt, `solution.md`.

- `bootstrap/setup.sh` creates the namespaces and runs `bootstrap/stage-node.sh`
  inside the lab's node container. The staging script draws a new random
  starting state on every start, so the answers cannot be memorised.
- `testing/live.py` recomputes the truth from the live state on every run and
  compares it with what the learner recorded. Nothing in the lab stores an
  answer key.
- `solution/apply.sh` is the reference solution that `astrona test` applies.

Run `astrona validate .` and `astrona test . --accept-terms --headless` in this
folder. `testing/verify-start.sh` checks that every outcome fails on the
starting state; after the reference solution every outcome must pass.
