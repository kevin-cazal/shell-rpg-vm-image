INTRO_TEXT="
 ____  _   _ _____ _     _       ____  ____   ____
/ ___|| | | | ____| |   | |     |  _ \|  _ \ / ___|
\___ \| |_| |  _| | |   | |     | |_) | |_) | |  _ 
 ___) |  _  | |___| |___| |___  |  _ <|  __/| |_| |
|____/|_| |_|_____|_____|_____| |_| \_\_|    \____|

Une aventure au terminal.
Explorez les zones, parlez aux PNJ,
progressez dans l'histoire."

export PATH=/tmp/bin:$PATH
[ -d /tmp/lib ] && export LD_LIBRARY_PATH="/tmp/lib${LD_LIBRARY_PATH:+:}$LD_LIBRARY_PATH"
[ -d /tmp/usr/lib ] && export LD_LIBRARY_PATH="/tmp/usr/lib${LD_LIBRARY_PATH:+:}$LD_LIBRARY_PATH"
export LANG=C.UTF-8
export LC_CTYPE=C.UTF-8

case "$(tty)" in
/dev/hvc0)
	_game_zone_bg_file() {
		case $(pwd) in
			/tmp/game_map/montagne/*/route_de_montagne/vallée/château/donjon) echo dungeon.png ;;
			/tmp/game_map/montagne/*/route_de_montagne/vallée/château/salle_du_trône) echo throne_room.png ;;
			/tmp/game_map/montagne/*/route_de_montagne/vallée/château/bibliothèque) echo library.png ;;
			/tmp/game_map/montagne/*/route_de_montagne/vallée/château) echo castle.png ;;
			/tmp/game_map/montagne/*/route_de_montagne/lac/fond_du_lac) echo lake_bottom.png ;;
			/tmp/game_map/montagne/*/route_de_montagne/lac) echo lake.png ;;
			/tmp/game_map/montagne/*/route_de_montagne/vallée) echo valley.png ;;
			/tmp/game_map/montagne/*/route_de_montagne) echo mountain_road.png ;;
			/tmp/game_map/montagne/tunnel) echo tunnel.png ;;
			/tmp/game_map/montagne/.passage_secret) echo secret_passage.png ;;
			/tmp/game_map/forêt/mer) echo sea.png ;;
			/tmp/game_map/forêt) echo forest.png ;;
			/tmp/game_map/montagne) echo mountain.png ;;
			/tmp/game_map/village) echo village.png ;;
			/tmp/game_map) echo root.png ;;
			*) echo "" ;;
		esac
	}

	_game_bg_clear() {
		[ -w /dev/hvc1 ] || return 0
		/usr/local/bin/vm-bridge-send bg clear
	}

	_game_bg_root() {
		[ -w /dev/hvc1 ] || return 0
		/usr/local/bin/vm-bridge-send bg root.png
	}

	_game_cd_notify_host() {
		[ -w /dev/hvc1 ] || return 0
		_bg=$(_game_zone_bg_file)
		if [ -n "$_bg" ]; then
			/usr/local/bin/vm-bridge-send "bg $_bg"
		else
			_game_bg_clear
		fi
	}

	trap _game_bg_root EXIT

	cd() {
		if [ $# -eq 0 ]; then
			set -- /tmp/game_map
		fi
		builtin cd "$@" || return
		_game_cd_notify_host
	}

	[ -t 0 ] && tty > /tmp/.rpg_tty
	;;
esac

case "$(tty)" in
/dev/hvc0)
	_SPLASH_WIDTH=0
	_SPLASH_MARGIN=0

	_splash_init_layout() {
		local _line _tc _term_cols=80
		_SPLASH_WIDTH=0
		while IFS= read -r _line || [ -n "$_line" ]; do
			[ -z "$_line" ] && continue
			[ "${#_line}" -gt "$_SPLASH_WIDTH" ] && _SPLASH_WIDTH=${#_line}
		done <<EOF
$INTRO_TEXT
EOF
		[ "$_SPLASH_WIDTH" -lt 1 ] && _SPLASH_WIDTH=51
		if [ -t 1 ]; then
			_tc=$(stty size 2>/dev/null | awk '{print $2}')
			[ -n "$_tc" ] && [ "$_tc" -gt 0 ] && _term_cols=$_tc
		fi
		_SPLASH_MARGIN=$(( (_term_cols - _SPLASH_WIDTH) / 2 ))
		[ "$_SPLASH_MARGIN" -lt 0 ] && _SPLASH_MARGIN=0
	}

	_center_splash_line() {
		local text=$1 len pad
		if [ -z "$text" ]; then
			printf '\n'
			return
		fi
		len=${#text}
		pad=$(( (_SPLASH_WIDTH - len) / 2 ))
		[ "$pad" -lt 0 ] && pad=0
		printf '%*s%s\n' "$((_SPLASH_MARGIN + pad))" '' "$text"
	}

	_draw_splash() {
		_splash_init_layout
		_game_bg_root
		printf '\033[?25l\033[H'
		while IFS= read -r _line || [ -n "$_line" ]; do
			_center_splash_line "$_line"
		done <<EOF
$INTRO_TEXT
EOF
		printf '\n'
		_center_splash_line '[Press Enter to start]'
	}

	trap 'printf "\033[?25h"; stty echo; trap - INT; return 130' INT
	stty -echo
	clear
	_draw_splash
	if [ -w /dev/hvc1 ] && [ ! -f /tmp/.splash_ready_sent ]; then
		touch /tmp/.splash_ready_sent
		/usr/local/bin/vm-bridge-send splash-ready
	fi
	while true; do
		if read -t 0; then
			read -rs
			break
		fi
		_draw_splash
		sleep 1
	done
	printf "\033[?25h"
	stty echo
	trap - INT

	;;
esac

case "$(tty)" in
/dev/hvc0)
	cd /tmp/game_map
	if mountpoint -q /mnt/host 2>/dev/null; then
		[ -r /tmp/player.json ] && \
			cp /tmp/player.json /mnt/host/player.json 2>/dev/null || true
	fi
	;;
esac
