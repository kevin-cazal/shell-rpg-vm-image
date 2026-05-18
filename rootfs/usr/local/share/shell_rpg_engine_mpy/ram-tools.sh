# POSIX sh — copy micropython/busybox and their .so deps into tmpfs (/tmp).
# Sourced by install.sh and game-ram-setup.

ram_copy_libs_for() {
	_bin="$1"
	[ -x "$_bin" ] || return 0
	ldd "$_bin" 2>/dev/null | while read -r _line; do
		_lib=""
		case "$_line" in
			*'=> '*) _lib=$(printf '%s\n' "$_line" | sed -n 's/.*=> \([^ (]*\).*/\1/p') ;;
			/lib/*|/usr/lib/*) _lib=$(printf '%s\n' "$_line" | awk '{print $1}') ;;
		esac
		[ -n "$_lib" ] || continue
		case "$_lib" in
			/lib/*|/usr/lib/*) ;;
			*) continue ;;
		esac
		[ -e "$_lib" ] || continue
		_dest="/tmp$_lib"
		mkdir -p "$(dirname "$_dest")"
		cp -Lf "$_lib" "$_dest" 2>/dev/null || cp -f "$_lib" "$_dest"
	done
}

ram_install_micropython_bin() {
	[ -x /usr/bin/micropython ] || return 0
	mkdir -p /tmp/bin
	cp -f /usr/bin/micropython /tmp/bin/micropython
	chmod 755 /tmp/bin/micropython
	if [ -n "${INSTALL_QUIET:-}" ] && [ "${INSTALL_QUIET}" != 0 ]; then
		printf .
	fi
	ram_copy_libs_for /usr/bin/micropython
	if [ -f /tmp/bin/engine.py ]; then
		sed -i '1s|^#!.*|#!/tmp/bin/micropython|' /tmp/bin/engine.py
	fi
}

ram_install_busybox_bin() {
	_bb=/bin/busybox
	[ -x "$_bb" ] || return 0
	mkdir -p /tmp/bin
	cp -f "$_bb" /tmp/bin/busybox
	chmod 755 /tmp/bin/busybox
	if [ -n "${INSTALL_QUIET:-}" ] && [ "${INSTALL_QUIET}" != 0 ]; then
		printf .
	fi
	ram_copy_libs_for "$_bb"
	for _applet in ls cat mkdir mv cp sort whoami pwd chmod less ln rm; do
		ln -sf busybox "/tmp/bin/$_applet"
		if [ -n "${INSTALL_QUIET:-}" ] && [ "${INSTALL_QUIET}" != 0 ]; then
			printf .
		fi
	done
}

ram_install_toolchain() {
	ram_install_micropython_bin
	ram_install_busybox_bin
}
