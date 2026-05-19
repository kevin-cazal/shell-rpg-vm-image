#!/bin/bash
set -e
ENGINE=$(basename -s .py "$1")
ENGINE="engine"
dot() { printf '.'; }

printf 'Setting up the game'
export INSTALL_QUIET=1

mkdir -p /tmp/bin
mkdir -p /tmp/bin/quests
for q in config.py lake_data.py npc_def.py path.py translation_tab.py treasure_base64.py; do
	cp "quests/$q" /tmp/bin/quests/
	dot
done
for f in "$ENGINE.py" compat.py quest_registry.py ui.py; do
	cp "$f" /tmp/bin/
	dot
done
for i in $(micropython -c "import sys; sys.path.insert(0,'/tmp/bin'); sys.path.insert(0,'/tmp/bin/quests'); import engine; print(*engine.ACTIONS.keys())"); do
	bin=/tmp/bin/$i
	rm -f "$bin"
	ln -sf "$ENGINE.py" "$bin"
	chmod +x "$bin"
	dot
done

export PATH=/tmp/bin:$PATH

rm -rf /tmp/game_map

micropython quests/npc_def.py

cat > /tmp/player.json << EOF
{
    "name": "Player",
    "level": 0,
    "base_dir": "/tmp/game_map",
    "quests": [],
    "quests_done": [],
    "commands": [
        {"type": "command", "name": "talk", "desc": "Parler à un PNJ (ex: talk toto.npc)"},
        {"type": "command", "name": "player", "desc": "Afficher le statut du joueur"},
        {"type": "command", "name": "cd <directory>", "desc": "Changer de répertoire (changer de zone) (ex: cd village)"},
        {"type": "command", "name": "cd ..", "desc": "Remonter d'un répertoire (retourner à la zone précédente)"},
        {"type": "command", "name": "ls", "desc": "Lister les fichiers et répertoires (observer ce qui se trouve dans la zone) (ex: ls)"}
    ],
    "stories": []
}
EOF
dot

[ -d /mnt/host ] && cp /tmp/player.json /mnt/host/player.json 2>/dev/null || true
dot

. "$(dirname "$0")/ram-tools.sh"
ram_install_toolchain

printf '\n'
