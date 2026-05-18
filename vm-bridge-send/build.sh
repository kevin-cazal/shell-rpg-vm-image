#!/bin/sh
set -e

if [ -z "${DOCKER_HOST:-}" ] && [ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/docker.sock" ]; then
	export DOCKER_HOST="unix://${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/docker.sock"
fi

cd "$(dirname "$0")"

IMAGE=vm-bridge-send-i386-alpine
CONTAINER=vm-bridge-send-i386-alpine-tmp

docker build --platform linux/386 -t "$IMAGE" -f Containerfile .
docker rm -f "$CONTAINER" 2>/dev/null || true
docker create --name "$CONTAINER" "$IMAGE"
STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING"' EXIT
docker cp "$CONTAINER:/out/vm-bridge-send" "$STAGING/vm-bridge-send"
docker cp "$CONTAINER:/out/vm-bridge-raw" "$STAGING/vm-bridge-raw"
docker cp "$CONTAINER:/out/vm-bridge-read" "$STAGING/vm-bridge-read"
docker cp "$CONTAINER:/out/vm-bridge-listen" "$STAGING/vm-bridge-listen"
docker rm "$CONTAINER"

strip "$STAGING"/vm-bridge-* 2>/dev/null || true

install -d ../rootfs/usr/local/bin
install -m 4755 "$STAGING/vm-bridge-send" ../rootfs/usr/local/bin/vm-bridge-send
install -m 4755 "$STAGING/vm-bridge-raw" ../rootfs/usr/local/bin/vm-bridge-raw
install -m 4755 "$STAGING/vm-bridge-read" ../rootfs/usr/local/bin/vm-bridge-read
install -m 4755 "$STAGING/vm-bridge-listen" ../rootfs/usr/local/bin/vm-bridge-listen

echo "Installed vm-bridge-send, -raw, -read, -listen (setuid root)"
