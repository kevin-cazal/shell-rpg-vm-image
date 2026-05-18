#!/bin/sh
# Build disk image + V86B bundle (local or CI). Disk step requires root.
set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
IMAGE_SIZE="${IMAGE_SIZE:-256M}"
IMAGE="${IMAGE:-$ROOT/alpine-bios-${IMAGE_SIZE}.img}"
STATE="${STATE:-${IMAGE%.img}.v86state}"
BUNDLE="${BUNDLE:-$ROOT/shell-rpg-256M.v86b}"
AMVI="${ALPINE_MAKE_VM_IMAGE:-$ROOT/alpine-make-vm-image/alpine-make-vm-image}"
V86_RUNNER="${V86_RUNNER:-$ROOT/../v86-runner}"

if [ ! -x "$AMVI" ]; then
	echo "Missing alpine-make-vm-image at $AMVI" >&2
	echo "Run: git submodule update --init" >&2
	exit 1
fi

if [ ! -d "$V86_RUNNER" ]; then
	echo "Missing v86-runner at $V86_RUNNER (set V86_RUNNER)" >&2
	exit 1
fi

export ALPINE_MAKE_VM_IMAGE="$AMVI"
export IMAGE_SIZE IMAGE

if [ "$(id -u)" -ne 0 ]; then
	echo "Building disk image as root…" >&2
	if command -v doas >/dev/null 2>&1; then
		doas -E env ALPINE_MAKE_VM_IMAGE="$AMVI" IMAGE_SIZE="$IMAGE_SIZE" IMAGE="$IMAGE" \
			"$ROOT/build.sh"
	else
		sudo -E env ALPINE_MAKE_VM_IMAGE="$AMVI" IMAGE_SIZE="$IMAGE_SIZE" IMAGE="$IMAGE" \
			"$ROOT/build.sh"
	fi
else
	"$ROOT/build.sh"
fi

echo "Building V86 state + bundle…"
(
	cd "$V86_RUNNER"
	if [ ! -d node_modules ]; then
		npm ci
	fi
	export VITE_VM_MEMORY_MB="${VITE_VM_MEMORY_MB:-256}"
	export V86_STATE_CONSOLE_COLS="${V86_STATE_CONSOLE_COLS:-80}"
	export V86_STATE_CONSOLE_ROWS="${V86_STATE_CONSOLE_ROWS:-24}"
	npm run build-bundle -- --disk "$IMAGE" --state "$STATE" -o "$BUNDLE"
)

echo "Done:"
echo "  $IMAGE"
echo "  $STATE"
echo "  $BUNDLE"
