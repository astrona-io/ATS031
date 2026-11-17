---
exam_objectives:
- Protect node metadata and endpoints
---
# Remove A Runtime Socket Mount Solution

## Inspect the starting state

List the host paths of every pod in the namespace, then look at the socket and the user id from inside the scanner pod:

```sh
kubectl -n dock-031-040-03-03 get pods -o jsonpath='{range .items[*]}{.metadata.name}{" "}{range .spec.volumes[*]}{.hostPath.path}{" "}{end}{"\n"}{end}'
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- id -u
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- ls -l /host/run/containerd/containerd.sock
```

The first command shows `/run/containerd` for the `image-scanner` pod and `/var/log` for the `log-shipper` pod. The second prints `0`, so the process runs as root. The third shows a file whose type letter is `s`, which marks a socket. A root process with this socket can ask containerd to start a new container that mounts the whole node.

## Fix the Deployment

The fix has three parts. Remove the `runtime` volume and its `volumeMounts` entry. Replace `runAsUser: 0` with `runAsNonRoot: true` and a numeric `runAsUser`, because the kubelet can only check `runAsNonRoot` against a numeric user id. Keep the `scratch` and `settings` volumes as they are.

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

The Deployment controller starts a new pod from the changed template and then removes the old pod. Running `kubectl edit deployment image-scanner -n dock-031-040-03-03` and making the same changes there gives the same result.

## Verify

Wait for the new pod, then repeat the checks from inside it:

```sh
kubectl -n dock-031-040-03-03 rollout status deployment/image-scanner
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- id -u
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- ls /host/run/containerd
kubectl -n dock-031-040-03-03 exec deploy/image-scanner -- cat /etc/scanner/targets
```

The user id is now `1000`. The `ls` command fails, because the path no longer exists in the container. The settings file still prints its two registry lines.

After recording your result, remove the independent lab with `astrona destroy ats-031-lab-040-03-03`.

## Common pitfalls

> [!WARNING]
> Changing the mount to `readOnly: true` does not help: a client can still write requests to a socket on a read-only mount. Removing the `volumeMounts` entry but keeping the volume, or the other way round, either leaves the path in the pod specification or makes the API server reject the Deployment. Setting `runAsNonRoot: true` without a numeric `runAsUser` can leave the new pod in `CreateContainerConfigError` when the image names its user only by name.
