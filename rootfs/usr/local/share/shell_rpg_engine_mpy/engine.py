#!/usr/bin/env micropython

import compat  # noqa: F401 — patches os.path, hashlib, base64 before other imports

import sys
import os
import json

_engine_file = __file__
_engine_parts = _engine_file.split("/")
_engine_dir = "/".join(_engine_parts[:-1]) if len(_engine_parts) > 1 else "."
_runtime_quests_dir = "/tmp/bin/quests"
_quests_dir = _engine_dir + "/quests"

for _p in (_engine_dir, _runtime_quests_dir, _quests_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import quest_registry
import ui

source_config = _quests_dir + "/config.py"
target_config = _runtime_quests_dir + "/config.py"
if not os.path.exists(target_config) and os.path.exists(source_config):
    compat.copyfile(source_config, target_config)

PLAYER_FILE = '/tmp/player.json'
_HOST_PUSH_SCRIPT = '/usr/local/share/shell_rpg_engine_mpy/vm-bridge-player-json.sh'


def _push_player_json_to_host():
    try:
        if os.stat(_HOST_PUSH_SCRIPT)[0] & 0o111:
            os.system(_HOST_PUSH_SCRIPT + ' >/dev/null 2>&1')
    except OSError:
        pass


def bold(text):
    return "\033[1m" + text + "\033[0m"


def _command_label(cmd):
    return cmd.get("name", cmd.get("value", ""))


def _reward_key(reward):
    if reward.get("type") == "command":
        return ("command", _command_label(reward))
    if reward.get("type") == "story":
        return ("story", reward.get("value", reward.get("desc", "")))
    return (reward.get("type"), id(reward))


intro_story = {
    "type": "story",
    "desc": "Vous vous réveillez dans un endroit inconnu. Autour de vous, des chemins s'étendent dans plusieurs directions.\n"
    "    Vous vous levez et vous commencez à regarder autour de vous.\n"
    "    Utilisez la commande 'ls' (tapez 'ls' au clavier suivi de la touche Entrée) pour observer ce qui vous entoure.\n"
    "    Utilisez la commande 'cd <directory>' pour vous déplacer dans une direction (ex: cd village).\n"
    "    Utilisez la commande 'talk <npc>' pour parler à un PNJ (ex: talk toto.npc).\n",
    "value": "Introduction à l'aventure"
}


class Zone:
    def __init__(self):
        self.name = os.getcwd()
        self.list_dir = os.listdir(self.name)

    def list_npcs(self):
        self.npcs = [NPC(i) for i in os.listdir(self.name) if i.endswith('.npc')]
        return self.npcs

    def list_zones(self):
        self.subzones = [d for d in self.list_dir if os.path.isdir(os.path.join(self.name, d))]

    def __repr__(self):
        return "Zone(name=" + self.name + ", npcs=" + str(self.npcs) + ")"


class Quest:
    def __init__(self, name, desc, *args, **kwargs):
        self.name = name
        self.desc = desc
        self.level = kwargs["level"]

    def get_name(self):
        return self.name

    def get_description(self):
        return self.desc

    def get_level(self):
        return self.level

    def __repr__(self):
        if self.level > 0:
            return "  - " + self.name + "\n    Description=" + self.desc
        return ""


class Player:
    def __init__(self, *args, **kwargs):
        if not self.load():
            self.level = 1
            self.quests = []
            self.quests_done = []
            self.commands = [
                {"type": "command", "name": "talk", "desc": "Parler à un PNJ (ex: talk toto.npc)"},
                {"type": "command", "name": "player", "desc": "Afficher le statut du joueur"},
                {"type": "command", "name": "cd <directory>", "desc": "Changer de répertoire (changer de zone) (ex: cd village)"},
                {"type": "command", "name": "cd ..", "desc": "Remonter d'un répertoire (retourner à la zone précédente)"},
                {"type": "command", "name": "ls", "desc": "Lister les fichiers et répertoires (observer ce qui se trouve dans la zone) (ex: ls)"},
            ]
            self.stories = []
            if len(args) > 0:
                self.base_dir = args[0]
            elif 'base_dir' in kwargs:
                self.base_dir = kwargs['base_dir']
            else:
                raise ValueError("Base directory must be specified for Player initialization.")
            self.save()

    def get_quests(self):
        return self.quests

    def get_quests_done(self):
        return self.quests_done

    def get_all_quests(self):
        return self.quests + self.quests_done

    def add_quest(self, quest):
        if quest not in self.quests and quest not in self.quests_done:
            if quest.get('level', 0) > 0:
                ui.notify(
                    "quest_new",
                    str(quest.get('name', None)) + " - " + str(quest.get('desc', None)),
                )
            self.quests.append(quest)
        self.save()

    def add_reward(self, rewards):
        existing = {_reward_key(c) for c in self.commands}
        existing |= {_reward_key(s) for s in self.stories}
        for reward in rewards:
            key = _reward_key(reward)
            if key in existing:
                continue
            if reward.get('type') == 'command':
                self.commands.append(reward)
                existing.add(key)
                ui.notify(
                    "reward_command",
                    "Nouvelle commande '" + _command_label(reward) + "' apprise, utilisez la commande 'player' pour voir la liste des commandes.",
                )
            elif reward.get('type') == 'story':
                self.stories.append(reward)
                existing.add(key)
                lore = reward.get('desc', '').strip()
                if not lore:
                    lore = "Nouvelle histoire débloquée, utilisez la commande 'player' pour voir l'histoire."
                ui.notify("reward_story", lore)
        self.save()

    def remove_quest(self, quest):
        if quest in self.quests:
            self.quests.remove(quest)
            if quest not in self.quests_done:
                self.quests_done.append(quest)
            ui.notify(
                "quest_done",
                "La quête '" + str(quest.get('name', None)) + "' a été complétée.",
            )
        self.save()

    def get_level(self):
        total = 0
        for q in self.get_quests_done():
            total += q["level"]
        return total

    def save(self):
        with open(PLAYER_FILE, 'w') as f:
            json.dump({
                'base_dir': self.base_dir,
                'level': self.get_level(),
                'quests': self.quests,
                'quests_done': self.quests_done,
                'commands': self.commands,
                'stories': self.stories
            }, f)
        _push_player_json_to_host()

    def load(self):
        try:
            with open(PLAYER_FILE, 'r') as f:
                data = json.load(f)
                self.base_dir = data.get('base_dir')
                self.level = data.get('level')
                self.quests = data.get('quests')
                self.quests_done = data.get('quests_done')
                self.commands = data.get('commands')
                self.stories = data.get('stories')
                return True
        except OSError:
            return False

    def _format_quest_lines(self, quests):
        lines = []
        for q in quests:
            if q.get("level", 0) > 0:
                lines.append("- " + q.get("name", "?"))
                desc = q.get("desc", "")
                if desc:
                    for part in desc.split("\n"):
                        part = part.strip()
                        if part:
                            lines.append("  " + part)
        return lines if lines else ["Aucune"]

    def _format_command_lines(self):
        lines = []
        for cmd in self.commands:
            lines.append("- " + _command_label(cmd) + ": " + cmd.get("desc", ""))
        return lines if lines else ["Aucune"]

    def _format_story_lines(self):
        lines = []
        intro = intro_story.get("desc", "").strip()
        if intro:
            for part in intro.split("\n"):
                part = part.strip()
                if part:
                    lines.append(part)
        for story in self.stories:
            desc = story.get("desc", "").strip()
            if desc:
                if lines:
                    lines.append("")
                for part in desc.split("\n"):
                    part = part.strip()
                    if part:
                        lines.append(part)
        return lines if lines else ["Aucune"]

    def _status_sections(self):
        return [
            ("main", "FICHE JOUEUR", [ui.format_level_line(self.get_level())]),
            ("quests_active", "Quêtes en cours", self._format_quest_lines(self.quests)),
            ("quests_done", "Quêtes terminées", self._format_quest_lines(self.quests_done)),
            ("commands", "Commandes", self._format_command_lines()),
            ("stories", "Histoire", self._format_story_lines()),
        ]

    def show_status(self):
        ui.show_player_status(self._status_sections())

    def __repr__(self):
        return "Player(level=" + str(self.get_level()) + ")"


class NPC:
    def __init__(self, name, *args):
        self.name = name
        self.json_data = self.load_npc_data()

    def load_npc_data(self):
        npc_file = os.path.join(os.getcwd(), self.name)
        if not os.path.exists(npc_file):
            raise OSError("NPC file " + npc_file + " does not exist.")
        with open(npc_file, 'r') as f:
            return json.load(f)

    def get_name(self):
        return self.name

    def get_quests(self):
        return list(self.json_data.get('quests', []))

    def __repr__(self):
        return "NPC(name=" + self.name + ")"

    def get_next_quest(self):
        quests = self.get_quests()
        if quests:
            return quests[0]
        return None

    def get_quest_validation_instance(self, quest_script):
        try:
            quest_val_class = quest_registry.resolve(quest_script)
            if quest_val_class is None:
                return None
            return quest_val_class(
                self.get_next_quest(),
                Player(),
                os.path.join(os.getcwd(), self.name),
            )
        except Exception:
            return None

    def check_quest(self, quest_script):
        quest_val_instance = self.get_quest_validation_instance(quest_script)
        if quest_val_instance:
            return quest_val_instance.validate_quest()
        return False, "Quest validation instance could not be created."

    def run_post_quest(self, quest_script):
        quest_val_instance = self.get_quest_validation_instance(quest_script)
        if quest_val_instance:
            quest_val_instance.post_quest()

    def check_done_quest_requirements(self, dep, player):
        requirements_met = 0
        for quest in player.get_quests_done():
            if quest.get('name') in dep:
                requirements_met += 1
        return requirements_met == len(dep)

    def check_doing_quest_requirements(self, dep, player):
        requirements_met = 0
        for quest in player.get_quests():
            if quest.get('name') in dep:
                requirements_met += 1
        return requirements_met == len(dep)

    def get_quest_setup_instance(self, setup_script):
        try:
            setup_class = quest_registry.resolve(setup_script)
            if setup_class is None:
                return None
            return setup_class(Player(), os.path.join(os.getcwd(), self.name))
        except Exception:
            return None

    def give_quest(self):
        quest_added = False
        player = Player()
        for npc_quest in self.get_quests():
            if npc_quest.get('name') not in [quest.get('name') for quest in player.get_all_quests()]:
                if self.check_done_quest_requirements(npc_quest.get('must_done', []), player) and \
                        self.check_doing_quest_requirements(npc_quest.get('must_doing', []), player):
                    quest_dialog = npc_quest.get('text', '')
                    npc_quest_setup = npc_quest.get('setup_script', None)
                    if npc_quest_setup:
                        setup_instance = self.get_quest_setup_instance(npc_quest_setup)
                        if setup_instance:
                            setup_instance.setup_quest()
                    ui.say_npc(self.name, quest_dialog)
                    player.add_quest(npc_quest)
                    if npc_quest.get('level', 0) == 0:
                        self.talk(intro=False)
                    quest_added = True
                    break
        return quest_added

    def talk(self, intro=True):
        player = Player()
        talk = self.json_data.get('talk', '')
        if talk and intro:
            ui.say_npc(self.name, talk)
        for player_quest in player.get_quests():
            if player_quest.get('name') in [quest.get('name') for quest in self.get_quests()]:
                quest_status, message = self.check_quest(player_quest.get('script'))
                ui.say_npc(self.name, message)
                if quest_status:
                    self.run_post_quest(player_quest.get('script'))
                    player.remove_quest(player_quest)
                    player.add_reward(player_quest.get('rewards', []))
                else:
                    ui.say_npc(self.name, "La quête n'est pas encore terminée.")
        if not self.give_quest():
            ui.notify("system", "Aucune autre quête disponible.")


ACTIONS = {
    'player': lambda args: Player(*args).show_status(),
    'talk': lambda args: NPC(*args).talk(),
}

if __name__ == "__main__":
    ACTIONS[os.path.basename(sys.argv[0])](sys.argv[1:])
