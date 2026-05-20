# shell-rpg-vm-image

Alpine rootfs and chroot setup for the Shell RPG guest (serial / v86 only — no X stack).

Zone backgrounds are **not** in this repo — see `assets/zone-bg/` in [shell-rpg](https://github.com/kevin-cazal/shell-rpg). The guest only sends PNG filenames over vm-bridge (`hvc1`).

## Prerequisites

- Linux host, root for image build
- `alpine-make-vm-image` on `PATH` or `ALPINE_MAKE_VM_IMAGE=/path/to/alpine-make-vm-image`

## Build

```sh
./rpg-inject-tty/build.sh
./vm-bridge-send/build.sh
./mount-host-share/build.sh
doas ./build.sh
```

Output: `alpine-bios-${IMAGE_SIZE}.img` in the repo directory (default **`IMAGE_SIZE=256M`**; use `IMAGE_SIZE=512M` for the legacy size).

### 256 MiB profile (default)

- Disk: `IMAGE_SIZE=256M` (default in `build.sh`)
- Guest RAM in the browser: set `VITE_VM_MEMORY_MB=256` when running the web UI (see `dev-run.sh`)

```sh
chmod +x dev-run.sh
./dev-run.sh
```

Requires a sibling [shell-rpg](https://github.com/kevin-cazal/shell-rpg) clone and `VITE_VM_MEMORY_MB` support in `v86-runner` (`vm/index.js`).

## Standalone vs submodule

Standalone: clone this repo and set `ALPINE_MAKE_VM_IMAGE`.

As submodule of [shell-rpg](https://github.com/kevin-cazal/shell-rpg): use the umbrella `build.sh` instead.

## Releases (CI)

GitHub Actions builds disk + state + bundle on **version tags** (`v*`) or **workflow_dispatch**.

```sh
git tag v0.1.0 && git push origin v0.1.0
```

Or: Actions → **Release VM artifacts** → Run workflow.

**Assets** (latest release):

- `alpine-bios-256M.img`
- `alpine-bios-256M.v86state`
- `shell-rpg-256M.v86b` — [download](https://github.com/kevin-cazal/shell-rpg-vm-image/releases/latest/download/shell-rpg-256M.v86b)

Local full build (root + sibling `v86-runner`):

```sh
git submodule update --init
./scripts/build-release.sh
```
