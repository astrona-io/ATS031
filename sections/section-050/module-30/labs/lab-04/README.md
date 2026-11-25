# Pin An Image By Digest And Prove It Runs

Author notes for the graded lab `ats-031-lab-050-03-04`. The learner reads `question.md` and,
after the attempt, `solution.md`.

- `config.yaml` preloads `docker.io/library/python:3.13-alpine` into the kind
  nodes. `bootstrap/setup.sh` creates the namespace and applies
  `bootstrap/manifests/deployment-relay.yaml`, a one-replica `relay`
  Deployment that runs the image by tag, and waits for the rollout. The digest
  the learner must pin is the one the kubelet reports in `imageID`.
- A preloaded image has no repository digest in containerd, so the kubelet
  would report a bare `sha256:` image ID. Before the Deployment starts,
  `setup.sh` adds the name `docker.io/library/python@sha256:<manifest digest>`
  to the image on every node with `ctr images tag`. The kubelet then reports
  that name as `imageID`, and the pinned reference resolves locally with no
  network access. The digest therefore depends on the loaded image and differs
  between machines.
- `testing/live.py` recomputes the truth from the live state on every run and
  compares it with what the learner recorded. Nothing in the lab stores an
  answer key.
- `solution/apply.sh` is the reference solution that `astrona test` applies.

Run `astrona validate .` and `astrona test . --accept-terms --headless` in this
folder. `testing/verify-start.sh` checks that every outcome fails on the
starting state; after the reference solution every outcome must pass.
