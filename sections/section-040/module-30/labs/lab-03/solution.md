# Remove A Runtime Socket Mount — Solution

You solve this lab by replacing the `image-scanner` Deployment with a version that has no runtime volume and runs as a numeric non-root user. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

List the host paths of every pod in the namespace, then look at the socket and the user id from inside the scanner pod:

```sh
kubectl -n dock-031-040-03-03 get pods -o jsonpath='{range .items[*]}{.metadata.name}{" "}{range .spec.volumes[*]}{.hostPath.path}{" "}{end}{"\n"}{end}'
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- id -u
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- ls -l /host/run/containerd/containerd.sock
```

The first command shows `/run/containerd` for the `image-scanner` pod and `/var/log` for the `log-shipper` pod. The second prints `0`, so the process runs as root. The third shows a file whose type letter is `s`, which marks a socket.

## Step 2: remove the runtime volume from the template (check `socket-removed`)

Remove the `runtime` volume and its `volumeMounts` entry together: a mount without its volume makes the API server reject the Deployment. In the same file, replace `runAsUser: 0` with `runAsNonRoot: true` and a numeric `runAsUser`, which Step 4 explains. Keep the `scratch` and `settings` volumes as they are.

Save this as `deployment-image-scanner.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-scanner
  namespace: dock-031-040-03-03
  labels:
    app: image-scanner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: image-scanner
  template:
    metadata:
      labels:
        app: image-scanner
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: scanner
        image: docker.io/curlimages/curl:8.11.1
        command:
        - sleep
        - '86400'
        securityContext:
          allowPrivilegeEscalation: false
        volumeMounts:
        - name: scratch
          mountPath: /scratch
        - name: settings
          mountPath: /etc/scanner
          readOnly: true
      volumes:
      - name: scratch
        emptyDir: {}
      - name: settings
        configMap:
          name: scanner-settings
```

Apply it:

```sh
kubectl apply -f deployment-image-scanner.yaml
```

Confirm that the template has only the two remaining volumes:

```sh
kubectl -n dock-031-040-03-03 get deployment image-scanner -o jsonpath='{.spec.template.spec.volumes[*].name}{"\n"}'
```

The command prints `scratch settings`.

## Step 3: wait for the new pod (check `socket-hidden`)

The Deployment controller starts a new pod from the changed template and then removes the old pod. The old pod keeps the socket until it is gone, so wait for the rollout, then look inside the new pod:

```sh
kubectl -n dock-031-040-03-03 rollout status deployment/image-scanner
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- ls /host/run/containerd
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- cat /etc/scanner/targets
```

The `ls` command fails with `ls: /host/run/containerd: No such file or directory`, because the path no longer exists in the container. The settings file still prints its two lines, `registry.dock.internal/cargo` and `registry.dock.internal/relay`.

## Step 4: confirm the non-root user (check `runs-as-non-root`)

`runAsNonRoot: true` tells the kubelet to refuse to start the container as user id 0. The kubelet can only check it against a numeric user id, so the file also sets `runAsUser: 1000`. `allowPrivilegeEscalation: false` stops the process from gaining more privileges than its user has:

```sh
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- id -u
```

The command prints `1000`.

## Step 5: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> Changing the mount to `readOnly: true` does not help: a client can still write requests to a socket on a read-only mount, and the checks reject any host path under `/run/containerd`, `/var/lib/containerd`, `docker.sock` or `crio`.
>
> Removing the `volumeMounts` entry but keeping the volume leaves the path in the pod specification. Wait for the rollout as well: the checks need exactly one running `image-scanner` pod, and that pod must not see `containerd.sock`.
>
> Setting `runAsNonRoot: true` without a numeric `runAsUser` can leave the new pod in `CreateContainerConfigError` when the image names its user only by name. Keep the `scratch` and `settings` mounts and leave `log-shipper` unchanged, because the checks compare both.
