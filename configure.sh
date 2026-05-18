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

step 'Set up default keymap'
setup-keymap fr fr

step 'Set up loopback only'
cat > /etc/network/interfaces <<-EOF
	iface lo inet loopback
EOF
ln -s networking /etc/init.d/net.lo

step 'Adjust rc.conf'
sed -Ei \
	-e 's/^[# ](rc_depend_strict)=.*/\1=NO/' \
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
# hvc0: virtio console (v86 web). ttyS0: serial automation.
sed -i 's|^ttyS0::.*|ttyS0::respawn:/sbin/agetty --autologin user42 -s ttyS0 115200 xterm|' /etc/inittab
grep -q '^hvc0::' /etc/inittab || \
	echo 'hvc0::respawn:/sbin/agetty --autologin user42 -s hvc0 115200 xterm' >> /etc/inittab
sed 's@tty1::respawn:.*@@g' -i /etc/inittab

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
chmod +x /usr/local/share/shell_rpg_engine_mpy/install.sh
chmod +x /usr/local/share/shell_rpg_engine_mpy/vm-bridge-player-json.sh
# install.sh runs at boot via game-ram-setup (RAM-backed /tmp/game_map).
# Zone backgrounds and fonts live in the web runner (hvc0/xterm), not on disk.

rm -rf /var/cache/apk/*

step 'RAM-backed game and filesystem tuning'
if [ -f /etc/fstab ]; then
	sed -i 's/\trelatime\t/\tnoatime\t/' /etc/fstab
	if ! grep -qE '[[:space:]]/tmp[[:space:]]' /etc/fstab; then
		printf '%s\n' 'tmpfs	/tmp	tmpfs	mode=1777,size=32M	0	0' >> /etc/fstab
	fi
fi
chmod +x /etc/init.d/game-ram-setup
rc-update add game-ram-setup boot
chmod 4755 /usr/local/bin/vm-bridge-send
chmod 4755 /usr/local/bin/vm-bridge-raw
chmod 4755 /usr/local/bin/vm-bridge-read
chmod 4755 /usr/local/bin/vm-bridge-listen
chmod +x /usr/local/sbin/vm-bridge-daemon
chmod +x /etc/init.d/game-vm-bridge
rc-update add game-vm-bridge default
rm -rf /tmp/game_map /tmp/bin /tmp/player.json /tmp/lib /tmp/usr
