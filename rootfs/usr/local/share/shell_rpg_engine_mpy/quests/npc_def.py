import sys

_file_parts = __file__.split("/")
_compat_dir = "/".join(_file_parts[:-2]) if len(_file_parts) >= 2 and _file_parts[-2] == "quests" else "/".join(_file_parts[:-1])
if _compat_dir not in sys.path:
    sys.path.insert(0, _compat_dir)
import compat  # noqa: F401 — patches os before path helpers

import os
import json
import hashlib

from config import T
from translation_tab import *
from lake_data import livres
from path import *

import ui


base = "/tmp/game_map"


def _install_quiet():
    # MicroPython os has getenv, not environ (compat may wrap os).
    v = ""
    try:
        v = os.getenv("INSTALL_QUIET", "") or ""
    except AttributeError:
        pass
    if not v:
        try:
            v = os.environ.get("INSTALL_QUIET", "")
        except AttributeError:
            v = "1" if __name__ == "__main__" else ""
    return str(v) not in ("", "0", "false", "None")


def _progress():
    if _install_quiet():
        sys.stdout.write(".")
        sys.stdout.flush()


def _map_path(base_dir, path):
    """Resolve under base_dir; create_zone paths are already absolute under base."""
    base_dir = os.path.normpath(base_dir)
    path = os.path.normpath(path)
    if path == base_dir or path.startswith(base_dir + "/"):
        return path
    return os.path.join(base_dir, path)


def find_parent_in_dict(obj, key, value):
    """Recursively find parent dicts that contain a specific key/value."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            # Check for a match at this level
            if k == key and v == value:
                results.append(obj)
            # Recurse deeper
            results.extend(find_parent_in_dict(v, key, value))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_parent_in_dict(item, key, value))
    return results


class QuestValidation:
    def __init__(self, quest, player, npc):
        self.player = player
        self.quest = quest
        self.npc = npc

    def pre_quest(self):
        pass

    def validate_quest(self):
        pass

    def post_quest(self):
        pass

class Checks:
    @staticmethod
    def get_subdir_count(path):
        return len([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])

    @staticmethod
    def input_str(prompt):
        return input(prompt).strip()

    @staticmethod
    def file_under_location(file_name, location):
        for root, dirs, files in os.walk(f"{base}/{location}"):
            if file_name in files:
                return True
        return False

    @staticmethod
    def _sha256_hex(data):
        return compat._sha256_hex(data)

    @staticmethod
    def file_hash_match(file_path, expected_hash):
        if not os.path.exists(file_path):
            return False
        with open(file_path, 'rb') as f:
            return Checks._sha256_hex(f.read()) == expected_hash


    @staticmethod
    def file_content_match(file_path, expected_content):
        if not os.path.exists(file_path):
            return False
        with open(file_path, 'r') as f:
            content = f.read().strip()
            return content == expected_content


    @staticmethod
    def has_duplicate_in_dir(original_file, target_dir):
        with open(original_file, 'rb') as f:
            original_hash = Checks._sha256_hex(f.read())
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file == os.path.basename(original_file):
                    continue
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    if Checks._sha256_hex(f.read()) == original_hash:
                        return True
        return False

    @staticmethod
    def file_is_a_symlink_to(file_path, target_path):
        if not os.path.islink(file_path):
            return False
        return os.readlink(file_path) == target_path

    def lines_in_file_sorted_alphabetically(file_path, expected_lines):
        if not os.path.exists(file_path):
            return False
        with open(file_path, 'r') as f:
            lines = f.read().strip().split('\n')
            return lines == expected_lines

class Mkdir(QuestValidation): # Quest giver: Kevin, Location: village
    def validate_quest(self):
        super().validate_quest()
        if Checks.get_subdir_count(village_path) >= 3:
            return True, f"Bravo ! Vous avez créé 3 maisons dans le {village[T]}."
        else:
            return False, f"Vous devez créer 3 maisons dans le {village[T]} en utilisant la commande mkdir."

class HiddenCreate(QuestValidation):  # Quest giver: Quentintin, Location: Village
    def validate_quest(self):
        super().validate_quest()
        hidden_dirs = [
            d for d in os.listdir(village_path)
            if d.startswith(".") and os.path.isdir(os.path.join(village_path, d))
        ]
        if hidden_dirs:
            hidden_path = os.path.join(village_path, hidden_dirs[0])
            os.system(f"mv {village_path}/Quentintin.npc {hidden_path}/")
            return True, f"Merci d'avoir créé une planque ({hidden_dirs[0]}) !"
        else:
            return False, "Crée-moi une planque (un dossier caché, commençant par '.')."

class Treasure(QuestValidation):
    def validate_quest(self):
        super().validate_quest()
        if os.path.isfile(f"{lac_path}/tresor.tar"):
            return True, "Tonnerre de tonnerres ! Merci d'avoir repêché ce sacré trésor, mais maintenant, bougre d'explorateur d'eau douce, il va falloir l'ouvrir, nom d'un bachibouzouk !"
        else:
            return False, f"Mille sabords ! Halte-là, moussaillons ! Ramenez ce trésor au bercail, droit au {lake[T]}, et plus vite que ça, espèces de marins d'eau douce !"

class TreasureOpen(QuestValidation): # Quest giver: Haddock, Location: Lake
    def validate_quest(self):
        super().validate_quest()
        if os.path.isfile(f"{lac_path}/parchemin_secret1.obj") and os.path.isfile(f"{lac_path}/parchemin_secret2.obj") and os.path.isfile(f"{lac_path}/parchemin_secret3.obj"):
            return True, "Tonnerre de Brest ! Bravo, moussaillon, tu as ouvert le trésor ! Mille millions de sabords, te voilà désormais en possession des  formules magiques... ça pourra te servir plus tard, ou que le diable m'emporte !"
        else:
            return False, f"Mille milliards de mille sabords ! N'oublie pas ta quête, moussaillon : ouvre le trésor et empare-toi des formules magiques, ou tu finiras marin d'eau douce à vie !"

class ReadFile(QuestValidation): # Quest giver: Kevin, Location: forest

    def validate_quest(self):
        super().validate_quest()
        if Checks.input_str(f"Veuillez lire le panneau pour moi : ") == f"cd ../{village[T]}":
            return True, "Merci d'avoir lu le panneau !"
        else:
            return False, f"Ce n'est pas ce qui est écrit sur le panneau ! Veuillez réessayer."

class WhoIsThere(QuestValidation): # Quest giver: Paul, Location: village

    def validate_quest(self):
        super().validate_quest()
        if Checks.input_str("Veuillez me donner votre nom : ") == compat.get_username():
            with open(f"{village_path}/outils.obj", 'w') as f:
                f.write("c047eaea91e27374")
            return True, "Merci de m'avoir donné votre nom !"
        else:
            return False, "Ce n'est pas votre nom ! Veuillez réessayer."

class Move(QuestValidation): # Quest giver: Jacques, Location: mountain

    def validate_quest(self):
        super().validate_quest()
        if Checks.file_under_location("Jacques.npc", village[T]) and not Checks.file_under_location("Jacques.npc", mountain[T]):
            return True, f"Enfin chez moi dans le {village[T]} !"
        else:
            return False, f"Veuillez m'aider à retourner au {village[T]}"

class Fedex1(QuestValidation):  # Quest giver: Ouvrier, Location: .passage_secret → tunnel

    def validate_quest(self):
        super().validate_quest()
        if Checks.file_content_match(f"{passage_secret_path}/outils.obj", "c047eaea91e27374") or Checks.file_content_match(f"{tunnel_path}/outils.obj", "c047eaea91e27374"):
            return True, "Merci d'avoir apporté les outils ! Recule un peu pour me laisser travailler"
        else:
            return False, f"Vous devez apporter les outils du {village[T]} au passage secret."

    def post_quest(self):
        if os.path.isdir(passage_secret_path):
            os.rename(passage_secret_path, tunnel_path)
        if os.path.isdir(route_de_montagne_path):
            os.chmod(route_de_montagne_path, 0o755)
        ui.request_cd(montagne_path)



class Copy(QuestValidation): # Quest giver: Merchant, Location: mountainroad

    def validate_quest(self):
        super().validate_quest()
        if Checks.has_duplicate_in_dir(f"{route_de_montagne_path}/roue.obj", f"{route_de_montagne_path}/"):
            return True, "Bravo ! Vous avez copié la bonne roue."
        else:
            return False, "Vous devez copier le contenu de la bonne roue."


class SortBooks(QuestValidation): # Quest giver: Servant, Location: castle

    def validate_quest(self):
        super().validate_quest()
        for file in os.listdir(bibliotheque_path):
            if file.endswith(".obj"):
                path = f"{bibliotheque_path}/{file}"
                attendu = "\n".join(sorted(livres)) + "\n"
                with open(path, "r") as f:
                    contenu = f.read()
                if contenu == attendu:
                    return True, "Merci d'avoir trié les livres !"
        return False, "Vous devez trier les livres dans la bibliothèque."


class Shortcut(QuestValidation): # Quest giver: Guard, Location: dungeon

    def validate_quest(self):
        super().validate_quest()
        dungeon_path = f"{donjon_path}"
        symlink_to_village = None
        for file in os.listdir(dungeon_path):
            abspath = f"/{donjon_path}/{file}"
            # print(abspath)
            if (os.path.exists(abspath) and os.path.islink(abspath) and os.path.isdir(abspath)):
                try:
                    original_path = os.readlink(abspath)
                    # print("Original path: ", original_path)
                    # print(f"chemin: /{base}/{village_path}")
                    if os.path.samefile(original_path, f"/{village_path}"):
                        symlink_to_village = abspath
                        break
                except:
                    continue
        if symlink_to_village:
            return True, f"Vous avez créé un raccourci vers le {village_path} !"
        else:
            return False, f"Vous devez créer un raccourci vers le {village_path}."


class HiddenFile(QuestValidation): # Quest giver: Kevin, Location: forest

    def validate_quest(self):
        super().validate_quest()
        with open(f"{base}/{forest[T]}/.carte_cachee.obj", "r") as f:
            file_content = f.read().strip()
        if Checks.input_str("Quel est le contenu de la carte du passage secret ?") == file_content:
            return True, "Vous avez trouvé la carte du passage secret !"
        else:
            return False, "Vous devez trouver la carte du passage secret dans la forêt."

    def post_quest(self):
        if os.path.isdir(passage_secret_path):
            os.chmod(passage_secret_path, 0o755)
        route = passage_route_path if os.path.isdir(passage_route_path) else route_de_montagne_path
        if os.path.isdir(route):
            os.chmod(route, 0o600)

class AlwaysValid(QuestValidation): # For any quest that is always valid: For example, to give something to the player or print some lore related messages and progress in the story.

    def validate_quest(self):
        return True, ""

def _npc_speaker(npc_path):
    return os.path.basename(npc_path).replace(".npc", "")


class AcceptShell(AlwaysValid):  # Quest giver: Pecheur, Location: mer
    def post_quest(self):
        super().post_quest()
        speaker = _npc_speaker(self.npc)
        ui.say_npc(
            speaker,
            "Quand Paul au village vous demandera votre nom, tapez whoami pour le connaître.",
        )


class KingSummons(AlwaysValid):  # Quest giver: Roi, Location: chateau
    def post_quest(self):
        throne_roi = f"{salle_du_trone_path}/Roi.npc"
        if os.path.exists(throne_roi):
            os.system(f"mv {throne_roi} {mer_for_path}/")
        mer_path = f"{mer_for_path}"
        for i in range(1, 4):
            with open(f"{mer_path}/brigand_{i}.brig", "w") as f:
                f.write("Un brigand menaçant se tient devant toi.")



class KingBrigandsManual(QuestValidation):  # Quest giver: Roi, Location: mer
    def validate_quest(self):
        super().validate_quest()

        brigands = [
            os.path.join(mer_for_path, "brigand_1.brig"),
            os.path.join(mer_for_path, "brigand_2.brig"),
            os.path.join(mer_for_path, "brigand_3.brig"),
        ]
        if all(not os.path.exists(b) for b in brigands):
            return True, "Bravo, tu as terrassé ces brigands un par un ! Mais d'autres vont arriver en masse..."
        else:
            return False, "Il reste encore des brigands sur la plage, élimine-les !"
    def post_quest(self):
        super().post_quest()
        for i in range(1, 101):
            with open(f"{mer_for_path}/brigand_{i}.brig", "w") as f:
                f.write("Un brigand menaçant se tient devant toi.")
        with open(f"{mer_for_path}/canon.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# /!\\ ATTENTION : cette commande détruit TOUT dans le répertoire courant\n")
            f.write("rm *\n")
        os.chmod(f"{mer_for_path}/canon.sh", 0o600)

class KingCanonIntro(QuestValidation):  # Quest giver: Roi, Location: mer
    def validate_quest(self):
        super().validate_quest()
        Roi_path = os.path.join(mer_for_path, "Roi.npc")

        Roi_vivant = os.path.exists(Roi_path)

        brigands_restants = [
            f for f in os.listdir(mer_for_path)
            if f.startswith("brigand_") and (f.endswith(".obj") or f.endswith(".brig"))
        ]
        plus_de_brigands = len(brigands_restants) == 0

        if Roi_vivant and plus_de_brigands:
            return True, "Victoire ! Les brigands ont été anéantis et je suis sauf. Le royaume est sauvé !"
        else:
            return False, "Les brigands ne sont pas tous éliminés, héros. Termine le travail !"

    def post_quest(self):
        with open("/tmp/chef_brigand", "w") as f:
            f.write(f"""
            #!/bin/bash
            while true; do
                NB_BRIG=`ls -l {mer_for_path} | grep -c '.brig'`
                [[ $NB_BRIG -lt 10 ]] && echo "Un brigand menaçant se tient devant toi." > brigand_$RANDOM.brig
                sleep $(($(($RANDOM % 10)) + 1))
            done
            """)
        os.system("chmod +x /tmp/chef_brigand")
        os.system("pgrep chef_brigand || /tmp/chef_brigand &")

class KillProcess(QuestValidation):
    def validate_quest(self):
        if os.system("pgrep chef_brigand") != 0:
            return True, "Le chef des brigands n'est plus là. Victoire !"
        else:
            return False, "Le chef des brigands est toujours là... Trouve son processus et arrête-le !"

class IsKing(QuestValidation):
    def validate_quest(self):
        super().validate_quest()
        Roi_path = f"{mer_for_path}/Roi.npc"
        if os.path.isfile(Roi_path):
            os.system(f"mv {mer_for_path}/Roi.npc {chateau_path}/")
            return True, "Ouf... tout va bien, il est là ! Mon coeur s'est arrêté... puis il a recommencé, de battre à nouveau. Sans lui, tout aurait sombré, mais sa présence éclaire encore nos ténèbres. Tant que le Roi respire, l'espoir du royaume vit encore ! \n BONNE FIN"
        else:
            return False, "Noooon... le Roi est mort ! Notre lumière s'est éteinte, et avec elle l'espoir du royaume... Qui nous protégera désormais des brigands et des tempêtes à venir ? Sans lui, le château n'est plus qu'un tombeau, et nous, de simples âmes perdues au milieu des ruines...\n MAUVAISE FIN"

class Story1(AlwaysValid):  # Quest giver: Kevin, Location: village
    pass


class Story2(AlwaysValid):  # Quest giver: Jacques, Location: mountain
    pass


class Story3(AlwaysValid):  # Quest giver: Worker, Location: .secret_passage
    pass


class Story4(AlwaysValid):  # Quest giver: Merchant, Location: mountainroad
    pass


class Story5(AlwaysValid):  # Quest giver: Quentintin, Location: Village
    pass

symlinks = []
post_ops = []
total_quests = 0
def create_zone(name, map_data):
    global symlinks
    global post_ops
    global total_quests
    for npcs in map_data.get("npcs", []):
        npc_path = os.path.join(name, compat.capitalize(npcs['name']) + ".npc")
        total_quests += len(npcs.get("quests", []))
        with open(npc_path, 'w') as npc_file:
            json.dump(npcs, npc_file)
        _progress()
    for obj in map_data.get("objects", []):
        if (obj['name'] == "tresor.tar"):
            obj_path = os.path.join(name, f"{obj['name'].lower()}")
        else:
            obj_path = os.path.join(name, f"{obj['name'].lower()}.obj")
        with open(obj_path, 'w') as obj_file:
            obj_file.write(obj['content'])
        _progress()
    for subzone in map_data.get("subzones", []):
        if subzone.get("name", None) is None:
            continue
        subzone_path = os.path.join(name, subzone['name'])
        symlink = subzone.get("symlink_to", None)
        if symlink:
            symlinks.append((subzone_path, symlink))
        else:
            os.makedirs(subzone_path, exist_ok=True)
            _progress()
            post_creation = subzone.get("post_creation", None)
            if (post_creation):
                post_ops.append((post_creation, subzone_path))
            create_zone(subzone_path, subzone)


def create_symlinks(base_dir):
    for link, target in symlinks:
        link_path = _map_path(base_dir, link)
        target_path = _map_path(base_dir, target)
        if not os.path.exists(target_path):
            if not _install_quiet():
                print(
                    f"Target {target_path} does not exist for symlink {link_path}, skipping.",
                    file=sys.stderr,
                )
            continue
        try:
            os.symlink(target_path, link_path)
            _progress()
        except FileExistsError:
            _progress()
        except Exception as e:
            if not _install_quiet():
                print(f"Error creating symlink {link_path}: {e}", file=sys.stderr)

def execute_post_ops():
    for func, arg in post_ops:
        try:
            func(arg)
            _progress()
        except Exception as e:
            if not _install_quiet():
                print(f"Error executing post operation on {arg}: {e}", file=sys.stderr)

def dump_map(json_data):
    with open("game_map.json", 'w') as f:
        json.dump(json_data, f)
    print("Game map dumped to game_map.json")

if __name__ == "__main__":
    import map
    base_dir = os.path.join("/tmp", "game_map")
    os.system("chmod -R u+rwx %s 2>/dev/null" % base_dir)
    os.system("rm -rf %s" % base_dir)
    os.makedirs(base_dir)
    create_zone(base_dir, map.MAP)
    create_symlinks(base_dir)
    execute_post_ops()
    if _install_quiet():
        sys.stdout.write("\n")
    else:
        print(f"Game map created at {base_dir} with total quests: {total_quests}")

