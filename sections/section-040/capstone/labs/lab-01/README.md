# Protect The Node Capstone

This graded capstone combines three skills in one cluster: blocking the cloud metadata address with one exception, closing the kubelet ports for pods, and removing a runtime socket mount. It uses a fake metadata server on the worker node, so every request in the task is real and every value is fake.

Start the cluster with the starting state in place:

```bash
astrona run --git git@github.com:astrona-io/ATS031.git -c sections/section-040/capstone/labs/lab-01
```

When you think you have finished, send it for grading:

```bash
astrona submit -c sections/section-040/capstone/labs/lab-01
```

When you are done, remove the lab:

```bash
astrona destroy ats-031-capstone-040
```

Run `testing/smoke.sh` with the private kubeconfig to verify that the starting state fails grading and that the reference result passes. Runtime verification has not been recorded yet.
