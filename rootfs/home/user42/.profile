export PATH=/tmp/bin:$PATH
[ -d /tmp/lib ] && export LD_LIBRARY_PATH="/tmp/lib${LD_LIBRARY_PATH:+:}$LD_LIBRARY_PATH"
[ -d /tmp/usr/lib ] && export LD_LIBRARY_PATH="/tmp/usr/lib${LD_LIBRARY_PATH:+:}$LD_LIBRARY_PATH"
export LANG=C.UTF-8
export LC_CTYPE=C.UTF-8

[ -f /usr/local/share/shell_rpg_engine_mpy/serial-debug.sh ] && \
	. /usr/local/share/shell_rpg_engine_mpy/serial-debug.sh

case "$(tty)" in
/dev/hvc0|/dev/ttyS0)
	[ -t 0 ] && tty > /tmp/.rpg_tty
	_i=0
	while [ ! -d /tmp/game_map ] && [ "$_i" -lt 90 ]; do
		sleep 1
		_i=$((_i + 1))
	done
	[ -d /tmp/game_map ] && cd /tmp/game_map
	[ -r /tmp/player.json ] && \
		/usr/local/share/shell_rpg_engine_mpy/vm-bridge-player-json.sh 2>/dev/null || true
	;;
esac
