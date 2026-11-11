---
draft: true
---
# Enforce An Address Exception And Port Range

Solve this question on: `terminal`

Three independent Pods in `ranges-training` provide a server and two clients. The server listens on TCP 8079 through 8083. No ingress policy restricts it yet.

Allow about 10 minutes for task work. Cluster startup adds time.

## Tasks

1. Create `bounded-range`, selecting only `app=range-server`, with ingress from `ipBlock.cidr: 0.0.0.0/0` except the current `excluded` Pod's single IPv4 address. Use `/32` for the exception.
2. Allow TCP 8080 through 8082 using `port` and `endPort`.
3. Verify the allowed client reaches all three ports, the excluded client cannot reach them, and neither adjacent port is reachable remotely.

## Constraints

Preserve Pods, their labels and every listener. Do not add another policy that broadens ingress. Pod addresses are used here only to demonstrate CIDR matching in a disposable Calico cluster; use selectors for production Pod identities.

## How the answer is checked

The grader checks the requested policy fields, confirms all local listeners are healthy, and opens fresh TCP connections from both clients. It tests both endpoints of the range, its middle, and adjacent ports.
