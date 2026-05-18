from translation_tab import *
from config import T
import os
import sys

base = "/tmp/game_map"

village_path = f"{base}/{village[T]}"
montagne_path = f"{base}/{mountain[T]}"
foret_path = f"{base}/{forest[T]}"
mer_for_path = f"{foret_path}/{sea[T]}"
tunnel_path = f"{montagne_path}/{tunnel[T]}"
route_de_montagne_path = f"{tunnel_path}/{mountain_road[T]}"
vallee_path = f"{route_de_montagne_path}/{valley[T]}"
lac_path = f"{route_de_montagne_path}/{lake[T]}"
mer_lac_path = f"{lac_path}/{sea[T]}"
fond_du_lac_path = f"{lac_path}/{lake_bottom[T]}"
passage_secret_path = f"{montagne_path}/{secret_passage[T]}"
# Before fedex1 renames .passage_secret → tunnel, route_de_montagne lives here.
passage_route_path = f"{passage_secret_path}/{mountain_road[T]}"
chateau_path = f"{vallee_path}/{castle[T]}"
bibliotheque_path = f"{chateau_path}/{library[T]}"
salle_du_trone_path = f"{chateau_path}/{throne_room[T]}"
donjon_path = f"{chateau_path}/{dungeon[T]}"

base_bg = "/usr/local/share/bg"

bg = {
		base: "root.png",
		village_path: "village.png",
		montagne_path: "mountain.png",
		foret_path: "forest.png",
		mer_for_path: "sea.png",
		tunnel_path: "tunnel.png",
		route_de_montagne_path: "mountain_road.png",
		vallee_path: "valley.png",
		lac_path: "lake.png",
		mer_for_path: "sea.png",
		fond_du_lac_path: "lake_bottom.png",
		passage_secret_path: "secret_passage.png",
		chateau_path: "castle.png",
		bibliotheque_path: "library.png",
		salle_du_trone_path: "throne_room.png",
		donjon_path: "dungeon.png"
}

if __name__ == "__main__":
	a = [' *)  printf "\\e]20;;\\a"  ;;']
	for k in bg.keys():
		img_path = os.path.join(base_bg, bg.get(k))
		a.insert(0, ' ' + k + ')  printf "\\e]20;' + img_path + ';100x100+50+50\\a"  ;;')
	print('\n'.join(['case $(pwd) in'] + a + ['esac']))
	sys.exit(0)
