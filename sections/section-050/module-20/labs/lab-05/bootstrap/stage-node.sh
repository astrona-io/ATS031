#!/usr/bin/env bash
# Runs inside the worker node container. Moves the running kubelet to a new
# path, chosen at random, through a systemd drop-in, and decides at random
# whether that copy matches the published v1.35.0 digest. /usr/bin/kubelet is
# left as a decoy that always gives the opposite answer. The published
# digests are the official sha256 values of the Kubernetes v1.35.0 release.
set -euo pipefail
release=/var/lib/kubelet-release
case "$(uname -m)" in
  x86_64) node_arch=amd64 ;;
  aarch64) node_arch=arm64 ;;
esac
declare -A official=(
  [amd64]=2f4ed7778681649b81244426c29c5d98df60ccabf83d561d69e61c1cbb943ddf
  [arm64]=aa658d077348b43d238f50966a583f4244b2a7d45590c77b3b165b7d44983ab8
)
if [[ "$(sha256sum /usr/bin/kubelet | cut -d' ' -f1)" != "${official[$node_arch]}" ]]; then
  echo "The node image kubelet is not the official v1.35.0 $node_arch build" >&2
  exit 1
fi
rm -rf "$release"
for arch in amd64 arm64; do
  mkdir -p "$release/v1.35.0/bin/linux/$arch" "$release/v1.34.3/bin/linux/$arch"
  printf '%s' "${official[$arch]}" > "$release/v1.35.0/bin/linux/$arch/kubelet.sha256"
  head -c 64 /dev/urandom | sha256sum | cut -d' ' -f1 | tr -d '\n' > "$release/v1.34.3/bin/linux/$arch/kubelet.sha256"
done
directory=$(printf '%s\n' /opt/node-agent /usr/local/lib/kubernetes /srv/kube-runtime /opt/k8s/node | shuf -n 1)
suffix=$(head -c 4 /dev/urandom | od -An -tx1 | tr -d ' \n')
running_binary="$directory/$suffix/kubelet"
rm -rf /opt/node-agent /usr/local/lib/kubernetes /srv/kube-runtime /opt/k8s
mkdir -p "$(dirname "$running_binary")"
cp /usr/bin/kubelet "$running_binary"
if (( RANDOM % 2 )); then
  # The running copy gets extra bytes after the end of the ELF file. It still
  # starts and reports v1.35.0, but its digest no longer matches.
  head -c 512 /dev/urandom >> "$running_binary"
else
  # The running copy is genuine; the unused /usr/bin/kubelet gets the bytes.
  # The kubelet still runs from /usr/bin/kubelet at this point, so the file
  # cannot be written in place: build the new file next to it and rename it.
  cp -p /usr/bin/kubelet /usr/bin/kubelet.new
  head -c 512 /dev/urandom >> /usr/bin/kubelet.new
  mv /usr/bin/kubelet.new /usr/bin/kubelet
fi
exec_line=$(grep '^ExecStart=/usr/bin/kubelet ' /etc/systemd/system/kubelet.service.d/10-kubeadm.conf)
{
  echo '[Service]'
  echo 'ExecStart='
  echo "${exec_line/\/usr\/bin\/kubelet/$running_binary}"
} > /etc/systemd/system/kubelet.service.d/20-node-agent.conf
touch -r /etc/systemd/system/kubelet.service.d/10-kubeadm.conf /etc/systemd/system/kubelet.service.d/20-node-agent.conf "$running_binary" /usr/bin/kubelet
systemctl daemon-reload
systemctl restart kubelet
for attempt in $(seq 1 60); do
  if [[ "$(readlink "/proc/$(pidof kubelet)/exe" 2>/dev/null)" == "$running_binary" ]]; then
    echo "kubelet runs from the new path"
    exit 0
  fi
  sleep 1
done
echo "kubelet did not start from the new path" >&2
exit 1
