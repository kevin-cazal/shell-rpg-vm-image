# shell-rpg-vm-image

Alpine rootfs and chroot setup for the Shell RPG guest (serial / v86 only — no X stack).

## Prerequisites

- Linux host, root for image build
- `alpine-make-vm-image` on `PATH` or `ALPINE_MAKE_VM_IMAGE=/path/to/alpine-make-vm-image`

## Build

```sh
./rpg-inject-tty/build.sh
./vm-bridge-send/build.sh
sudo ./build.sh
```

Output: `alpine-bios-YYYY-MM-DD.img` in the repo directory (override with `IMAGE=/path/to/disk.img`).

## Standalone vs submodule

Standalone: clone this repo and set `ALPINE_MAKE_VM_IMAGE`.

As submodule of [shell-rpg](https://github.com/kevin-cazal/shell-rpg): use the umbrella `build.sh` instead.
