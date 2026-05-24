#!/bin/sh
set -e

if [ -z "${DOCKER_HOST:-}" ] && [ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/docker.sock" ]; then
	export DOCKER_HOST="unix://${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/docker.sock"
fi

cd "$(dirname "$0")"

IMAGE=mount-host-share-i386-alpine
CONTAINER=mount-host-share-i386-alpine-tmp

docker build --platform linux/386 -t "$IMAGE" -f Containerfile .
docker rm -f "$CONTAINER" 2>/dev/null || true
docker create --name "$CONTAINER" "$IMAGE"
STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING"' EXIT
docker cp "$CONTAINER:/out/mount-host-share" "$STAGING/mount-host-share"
docker rm "$CONTAINER"

strip "$STAGING/mount-host-share" 2>/dev/null || true

install -d ../rootfs/usr/local/sbin
install -m 4755 "$STAGING/mount-host-share" ../rootfs/usr/local/sbin/mount-host-share

echo "Installed mount-host-share (setuid root)"
