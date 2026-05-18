#!/bin/bash
ENGINE=$(basename -s .py "$1")
ENGINE="engine"
echo "Please wait while setting up the environment..."
mkdir -p /tmp/bin
mkdir -p /tmp/bin/quests
# Runtime quest modules only (map.py/all.py used at build time from this directory).
for q in config.py lake_data.py npc_def.py path.py translation_tab.py treasure_base64.py; do
    cp "quests/$q" /tmp/bin/quests/
done
cp "$ENGINE.py" compat.py quest_registry.py ui.py /tmp/bin/
for i in $(micropython -c "import sys; sys.path.insert(0,'/tmp/bin'); sys.path.insert(0,'/tmp/bin/quests'); import engine; print(*engine.ACTIONS.keys())"); do
    bin=/tmp/bin/$i
    unlink "$bin" 2>/dev/null
    ln -sf "$ENGINE.py" "$bin"
    chmod +x "$bin"
done

export PATH=/tmp/bin:$PATH

# Reset map (fedex1 may chmod zones 600 or rename .passage_secret → tunnel).
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

/usr/local/share/shell_rpg_engine_mpy/vm-bridge-player-json.sh 2>/dev/null || true

. "$(dirname "$0")/ram-tools.sh"
ram_install_toolchain
if [ -d /usr/local/share/bg ]; then
    mkdir -p /tmp/bg
    cp -r /usr/local/share/bg/. /tmp/bg/
fi
