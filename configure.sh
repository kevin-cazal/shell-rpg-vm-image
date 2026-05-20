#!/bin/sh
set -eu

_step_counter=0
step() {
	_step_counter=$(( _step_counter + 1 ))
	printf '\n\033[1;36m%d) %s\033[0m\n' $_step_counter "$@" >&2
}

uname -a

step 'Set up timezone'
setup-timezone -z Europe/Paris

step 'Set up loopback only'
cat > /etc/network/interfaces <<-EOF
	iface lo inet loopback
EOF
ln -s networking /etc/init.d/net.lo

step 'Adjust rc.conf'
sed -Ei \
	-e 's/^[# ](rc_depend_strict)=.*/\1=YES/' \
	-e 's/^[# ](rc_parallel)=.*/\1=NO/' \
	-e 's/^[# ](rc_logger)=.*/\1=YES/' \
	-e 's/^[# ](unicode)=.*/\1=YES/' \
	/etc/rc.conf

step 'Enable services'
rc-update add net.lo boot
rc-update add termencoding boot

step 'Create non-root user'
adduser -D -s /bin/bash -h /home/user42 user42
addgroup user42 video
addgroup user42 input
addgroup user42 tty
chown -R user42:user42 /home/user42/

step 'Setup autologin'
# hvc0: user42 (game UI). ttyS0: root (serial / headless state quiesce). OpenRC after game-ram-setup.
sed -i '/^hvc0::/d; /^ttyS0::/d; /^tty1::respawn:/d' /etc/inittab
chmod +x /etc/init.d/agetty-hvc0 /etc/init.d/agetty-ttyS0
rc-update add agetty-hvc0 default
rc-update add agetty-ttyS0 default

# hvc0 last so /dev/console and OpenRC logs go to virtio console.
sed -Ei \
	-e 's|^[# ]*(default_kernel_opts)=.*|\1="console=tty0 console=hvc0"|' \
	/etc/update-extlinux.conf
update-extlinux

step 'Game engine image setup'
echo "dev.tty.legacy_tiocsti = 1" > /etc/sysctl.d/local.conf
if [ ! -x /usr/local/bin/rpg-inject-tty ]; then
	echo "rpg-inject-tty missing: run rpg-inject-tty/build.sh before building the image" >&2
	exit 1
fi
if [ ! -x /usr/local/sbin/mount-host-share ]; then
	echo "mount-host-share missing: run mount-host-share/build.sh before building the image" >&2
	exit 1
fi
chmod +x /usr/local/share/shell_rpg_engine_mpy/install.sh
# install.sh runs at boot via game-ram-setup (RAM-backed /tmp/game_map).
# Zone backgrounds and fonts live in the web runner (hvc0/xterm), not on disk.

rm -rf /var/cache/apk/*

step 'RAM-backed game and filesystem tuning'
if [ -f /etc/fstab ]; then
	sed -i 's/\trelatime\t/\tnoatime\t/' /etc/fstab
	if ! grep -qE '[[:space:]]/tmp[[:space:]]' /etc/fstab; then
		printf '%s\n' 'tmpfs	/tmp	tmpfs	mode=1777,size=32M	0	0' >> /etc/fstab
	fi
	# host9p is mounted at runtime (mount-host9p / mount-host-share), not via fstab:
	# v86 save_state keeps the guest mount but not the browser VFS — fstab mount + resume breaks.
fi
mkdir -p /mnt/host
# Load 9p modules before mount-host9p (OpenRC boot).
mkdir -p /etc/modules-load.d
printf '%s\n' 9p 9pnet_virtio > /etc/modules-load.d/host9p.conf
chmod +x /etc/init.d/mount-host9p
chmod +x /etc/init.d/game-ram-setup
rc-update add mount-host9p boot
rc-update add game-ram-setup boot
chmod 4755 /usr/local/bin/vm-bridge-send
chmod 4755 /usr/local/bin/vm-bridge-raw
chmod 4755 /usr/local/bin/vm-bridge-read
chmod 4755 /usr/local/bin/vm-bridge-listen
chmod +x /usr/local/sbin/vm-bridge-daemon
chmod +x /etc/init.d/game-vm-bridge
rc-update add game-vm-bridge default
rm -rf /tmp/game_map /tmp/bin /tmp/player.json /tmp/lib /tmp/usr
