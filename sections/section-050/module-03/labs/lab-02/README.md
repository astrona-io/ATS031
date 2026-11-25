# Verify A Signed apt Repository And An Installed Package

Author notes for the graded lab `ats-031-lab-050-03-02`. The learner reads `question.md` and,
after the attempt, `solution.md`.

- `bootstrap/setup.sh` creates the namespace and runs
  `bootstrap/build-repository.sh` in a throwaway `buildpack-deps` container with
  `--network none` on the host. It builds four `.deb` packages, a signed
  `Release` file and a keyring, and streams them into `/var/lib/fleet-apt` on
  the control plane node. `bootstrap/stage-node.sh` then installs
  `fleet-tools` with `dpkg -i`, changes one installed file and damages one
  `.deb`, both chosen at random. The host pulls the builder image if missing.
- `testing/live.py` recomputes the truth from the live state on every run and
  compares it with what the learner recorded. Nothing in the lab stores an
  answer key.
- `solution/apply.sh` is the reference solution that `astrona test` applies.

Run `astrona validate .` and `astrona test . --accept-terms --headless` in this
folder. `testing/verify-start.sh` checks that every outcome fails on the
starting state; after the reference solution every outcome must pass.
