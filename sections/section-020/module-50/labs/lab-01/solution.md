# Secure Kubelet Authentication And Authorization — Solution

You solve this lab with two edits to the kubelet configuration file and a kubelet restart. Keep `astrona submit --watch` running in a second terminal: it grades the lab again and again while you work and records nothing. Each check below turns green as you finish its task.

## Step 1: look at the starting state

The kubelet API on port `10250` can list pods, read logs and run commands in containers. Send a request without credentials from the node itself:

```sh
node_ip="$(kubectl get node "$(hostname)" -o jsonpath='{.status.addresses[?(@.type=="InternalIP")].address}')"
sudo curl -sk --max-time 5 -o /dev/null -w '%{http_code}\n' "https://$node_ip:10250/pods"
sudo grep -A6 '^authentication:' /var/lib/kubelet/config.yaml
sudo grep -A1 '^authorization:' /var/lib/kubelet/config.yaml
```

The request returns `200`: the kubelet accepts the anonymous request and allows it. Two settings work together here. Authentication decides who the caller is; with `anonymous.enabled: true`, a caller without credentials becomes the user `system:anonymous`. Authorization decides what the caller may do; `AlwaysAllow` allows everything.

Keep a copy of the file before you change it:

```sh
sudo cp /var/lib/kubelet/config.yaml /root/kubelet-config.yaml.before
```

## Step 2: turn off anonymous authentication (check `anonymous-auth`)

Open the file with `sudo vi /var/lib/kubelet/config.yaml`. Under `authentication:`, change the line `enabled: true` right below `anonymous:` to `false`, so the block reads:

```yaml
authentication:
  anonymous:
    enabled: false
```

The same edit as one command:

```sh
sudo sed -i '/^  anonymous:/{n;s/enabled: true/enabled: false/}' /var/lib/kubelet/config.yaml
```

This `sed` command finds the line `anonymous:` and changes `enabled` on the next line. Leave the `webhook` and `x509` entries under `authentication:` as they are.

## Step 3: authorize requests through the API server (check `webhook-authorization`)

Under `authorization:`, change `mode: AlwaysAllow` to `Webhook`, so the block starts with:

```yaml
authorization:
  mode: Webhook
```

The same edit as one command:

```sh
sudo sed -i 's/^  mode: AlwaysAllow$/  mode: Webhook/' /var/lib/kubelet/config.yaml
```

With `Webhook`, the kubelet sends each request to the API server as a `SubjectAccessReview` and follows its answer.

## Step 4: restart the kubelet (check `anonymous-request-rejected`)

The kubelet reads its configuration only when it starts:

```sh
sudo systemctl restart kubelet
```

Now a caller without credentials has no identity, so the kubelet rejects the request before it asks for authorization.

## Step 5: test the result

Read the effective configuration through the API server. The `configz` endpoint returns the values that the running kubelet really uses, after all sources are merged:

```sh
kubectl get --raw "/api/v1/nodes/$(hostname)/proxy/configz" | python3 -m json.tool | grep -A2 -e '"anonymous"' -e '"authorization"'
sudo curl -sk --max-time 5 -o /dev/null -w '%{http_code}\n' "https://$node_ip:10250/pods"
kubectl get node "$(hostname)"
```

`anonymous` shows `"enabled": false` and the mode is `"Webhook"`. The request now returns `401` (Unauthorized). The node is `Ready`. If the old values still show, wait a few seconds for the kubelet and run the commands again. The API server still reaches the kubelet with its own client certificate, so `kubectl logs` and `kubectl exec` keep working.

## Step 6: submit

When `astrona submit --watch` shows every check passing, stop it and run `astrona submit`. This grades the lab for real, ends the attempt and removes the lab.

## Common pitfalls

> [!WARNING]
> With only `Webhook` and anonymous access still on, the request returns `403` instead of `401`; the caller is still accepted as `system:anonymous`.
>
> A changed file without a kubelet restart changes nothing. The grader reads the effective configuration of the running kubelet.
>
> A typing mistake in `config.yaml` stops the kubelet, and a node that is not `Ready` fails every check. Keep the copy so you can put it back.
