#!/bin/sh
# Build the 256M disk image (if needed) and start the shell-rpg Vite dev server.
set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
SHELL_RPG="${SHELL_RPG:-$SCRIPT_DIR/../shell-rpg}"
IMAGE="${IMAGE:-$SCRIPT_DIR/alpine-bios-256M.img}"
export IMAGE_SIZE=256M
export IMAGE
export VITE_VM_MEMORY_MB=256

if [ ! -d "$SHELL_RPG" ]; then
	echo "Set SHELL_RPG to your shell-rpg clone (default: ../shell-rpg)" >&2
	exit 1
fi

if [ ! -f "$IMAGE" ] || [ "${FORCE_BUILD:-}" = 1 ]; then
	echo "Building VM image ($IMAGE_SIZE disk) → $IMAGE"
	if command -v doas >/dev/null 2>&1; then
		doas env IMAGE_SIZE="$IMAGE_SIZE" IMAGE="$IMAGE" "$SCRIPT_DIR/build.sh"
	else
		sudo -E "$SCRIPT_DIR/build.sh"
	fi
fi

ln -sf "$IMAGE" "$SHELL_RPG/alpine-bios-256M.img"

cd "$SHELL_RPG"
if [ ! -d submodules/v86-runner/node_modules ]; then
	(cd submodules/v86-runner && npm install)
fi
if [ ! -d node_modules ]; then
	npm install
fi
npm run prepare

echo ""
echo "Starting dev server (VM RAM: ${VITE_VM_MEMORY_MB} MiB, disk image: $IMAGE)"
echo "Open the app and choose: alpine-bios-256M.img"
echo ""

exec npm run dev
