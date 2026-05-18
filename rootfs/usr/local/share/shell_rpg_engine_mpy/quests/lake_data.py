import sys

_file_parts = __file__.split("/")
_compat_dir = "/".join(_file_parts[:-2]) if len(_file_parts) >= 2 and _file_parts[-2] == "quests" else "/".join(_file_parts[:-1])
if _compat_dir not in sys.path:
    sys.path.insert(0, _compat_dir)
import compat  # noqa: F401

import random
from compat import base64
from treasure_base64 import treasure_base64

livres = [
    "Germinal",
    "Madame Bovary",
    "Les Miserables",
    "LEtranger",
    "La Chartreuse de Parme",
    "Voyage au bout de la nuit",
    "Candide",
    "La Peste",
    "Notre-Dame de Paris",
    "Le Pere Goriot",
    "Jacques le Fataliste",
    "Bel-Ami",
    "Le Comte de Monte-Cristo",
    "La Princesse de Cleves",
    "Une vie",
    "La Condition humaine",
    "Therese Raquin",
    "Les Fleurs du mal",
    "Aurelien",
    "Les Chants de Maldoror",
    "La Fortune des Rougon",
    "Les Rois maudits",
    "Le Rouge et le Noir",
    "Sylvie",
    "Indiana",
    "La Symphonie pastorale",
    "La Guerre de TRoie naura pas lieu",
    "Phedre",
    "Cyrano de Bergerac",
    "Les Nourritures terrestres",
    "Manon Lescaut",
    "Discours de la methode",
    "Le Mariage de Figaro",
    "La Mare au diable",
    "Les Confessions",
    "LAssommoir",
    "La Nausee",
    "LIle mysterieuse",
    "La Chartreuse du Nord",
    "Le Soulier de satin",
    "Colomba",
    "Meditations poetiques",
    "Le Livre de ma mere",
    "La Disparition",
    "Enfance",
    "Le Hussard sur le toit",
    "Les Justes",
    "Le Diable au corps",
    "Le Deuxieme Sexe",
]


def create_lake_files(n=200):
    random.seed(42)
    objects = [
        "epave", "planche", "masque", "chaussure", "perle",
        "barque", "corail", "filet", "baril",
        "couvercle", "seau", "statue", "pagaie", "ancre", "pierre",
        "couronne", "seau_rouille", "lampe", "harnais",
        "crane", "os", "cloche",
        "parchemin", "boussole", "lanterne", "coquille", "roseau",
        "carpe", "brochet", "grenouille", "seau_perce", "pirogue",
        "seau_bois", "tesson",
        "idole", "coing", "bois_mouille", "seau_bois",
        "parfum", "poterie",
        "seau_argile", "tapis", "voile", "cordage", "carquois",
        "bouee", "chaudron", "seau_plomb", "chaussure_boueuse",
        "epingle", "clou", "poignee", "parasol",
        "seau_metal", "tabouret", "pied_statue", "tronc", "branche", "plume",
        "os_poisson", "sceau", "tombe", "pierre_gravee",
    ]

    obj = []
    for i in range(1, n + 1):
        name = f"{random.choice(objects)}_{i}"
        obj.append({
            "name": name,
            "desc": f"Un(e) {name} sans aucune utilité",
            "content": f"Un(e) {name} sans aucune utilité\n",
        })
    obj.append({
        "name": "tresor.tar",
        "desc": "Un trésor mysterieux en format .tar, contenant des formules magiques.",
        "content": base64.b64decode(treasure_base64).decode("utf-8"),
    })
    return obj
