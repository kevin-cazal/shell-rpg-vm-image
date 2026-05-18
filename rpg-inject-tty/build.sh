#!/bin/sh
set -e

# Rootless Docker uses a user-scoped socket.
if [ -z "${DOCKER_HOST:-}" ] && [ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/docker.sock" ]; then
	export DOCKER_HOST="unix://${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/docker.sock"
fi

cd "$(dirname "$0")"

IMAGE=rpg-inject-tty-i386-alpine
CONTAINER=rpg-inject-tty-i386-alpine-tmp

docker build --platform linux/386 -t "$IMAGE" -f Containerfile .
docker rm -f "$CONTAINER" 2>/dev/null || true
docker create --name "$CONTAINER" "$IMAGE"
rm -rf ./staging
mkdir -p ./staging
docker cp "$CONTAINER:/out/rpg-inject-tty" ./staging/rpg-inject-tty
docker rm "$CONTAINER"

strip ./staging/rpg-inject-tty 2>/dev/null || true

install -d ../rootfs/usr/local/bin
install -m 755 ./staging/rpg-inject-tty ../rootfs/usr/local/bin/rpg-inject-tty

echo "Installed ../rootfs/usr/local/bin/rpg-inject-tty ($(wc -c < ../rootfs/usr/local/bin/rpg-inject-tty) bytes)"
