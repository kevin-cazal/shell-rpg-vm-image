# cd hook: mlterm zone backgrounds and host bridge notifications.
. /usr/local/share/shell_rpg_engine_mpy/zone-bg.sh

cd() {
	if [ $# -eq 0 ]; then
		set -- /tmp/game_map
	fi
	builtin cd "$@" || return
	case "${TERM:-}" in
		rxvt-unicode-256color|mlterm|mlterm-256color|xterm|xterm-256color)
			_game_cd_set_bg_mlterm
			;;
	esac
	_game_cd_notify_host
}
