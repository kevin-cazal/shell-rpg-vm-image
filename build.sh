#!/bin/sh
set -eu

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
IMAGE_SIZE="${IMAGE_SIZE:-256M}"
IMAGE="${IMAGE:-$SCRIPT_DIR/alpine-bios-${IMAGE_SIZE}.img}"
AMVI="${ALPINE_MAKE_VM_IMAGE:-$SCRIPT_DIR/../alpine-make-vm-image/alpine-make-vm-image}"

on_build_exit() {
	ec=$?
	trap - EXIT
	if [ "$ec" -ne 0 ] && [ -f "$IMAGE" ]; then
		echo "Build failed (exit $ec); removing incomplete image: $IMAGE" >&2
		rm -f "$IMAGE"
	fi
	exit "$ec"
}
trap on_build_exit EXIT

if [ "$(id -u)" -ne 0 ]; then
	echo "Re-run as root (e.g. doas $0 or sudo $0)" >&2
	exit 1
fi

if [ ! -x "$AMVI" ]; then
	echo "Missing alpine-make-vm-image: set ALPINE_MAKE_VM_IMAGE" >&2
	exit 1
fi

if [ -f "$IMAGE" ] && command -v lsof >/dev/null 2>&1; then
	for pid in $(lsof -t "$IMAGE" 2>/dev/null); do
		kill "$pid" 2>/dev/null || true
	done
	sleep 1
fi

if [ -z "${APK:-}" ] && [ -x /tmp/apk-extract/sbin/apk.static ]; then
	export APK=/tmp/apk-extract/sbin/apk.static
fi

"$SCRIPT_DIR/rpg-inject-tty/build.sh"
"$SCRIPT_DIR/vm-bridge-send/build.sh"
"$SCRIPT_DIR/mount-host-share/build.sh"

rm -f "$IMAGE"

"$AMVI" \
	--arch x86 \
	--serial-console \
	--image-format raw \
	--image-size "$IMAGE_SIZE" \
	--repositories-file "$SCRIPT_DIR/repositories" \
	--packages "$(cat "$SCRIPT_DIR/packages")" \
	--fs-skel-dir "$SCRIPT_DIR/rootfs" \
	--fs-skel-chown root:root \
	--script-chroot \
	"$IMAGE" -- "$SCRIPT_DIR/configure.sh"

echo "Built: $IMAGE"
