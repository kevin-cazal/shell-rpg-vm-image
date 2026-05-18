# Zone → background filename for the browser host (vm-bridge on hvc1).

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

_game_cd_notify_host() {
	[ -w /dev/hvc1 ] || return 0
	_bg=$(_game_zone_bg_file)
	if [ -n "$_bg" ]; then
		/usr/local/bin/vm-bridge-send "bg $_bg"
	else
		/usr/local/bin/vm-bridge-send bg clear
	fi
}
