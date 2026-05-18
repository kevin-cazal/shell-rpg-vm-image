# cd hook: notify browser host of zone background changes (hvc1 vm-bridge).
. /usr/local/share/shell_rpg_engine_mpy/zone-bg.sh

cd() {
	if [ $# -eq 0 ]; then
		set -- /tmp/game_map
	fi
	builtin cd "$@" || return
	_game_cd_notify_host
}
