import os
from lake_data import create_lake_files, livres
import translation_tab
from path import *
from config import T

MAP =  {
     "subzones": [
        {
            "name": village[T],
            "npcs":
            [
                {
                    "name": "Kevin",
                    "talk": f"Salut l'artiste ! Toujours prêt à bricoler dans le {village[T]} ?",
                    "quests":
                    [
                        {
                            "name": "mkdir",
                            "must_done": [],
                            "text": f"Le {village[T]} est en ruines, nous devons le reconstruire. Pouvez-vous nous aider ? Utilisez la commande mkdir pour créer 3 répertoires (maisons) dans le {village[T]}.",
                            "desc": f"Aidez à reconstruire le {village[T]}. Créez 3 maisons dans le {village[T]}.",
                            "level": 1,
                            "script": "quests.npc_def.Mkdir",
                            "rewards": [
                                {
                                    "type": "command",
                                    "name": "cat <file>",
                                    "desc": "Lire le contenu d'un fichier",
                                },
                                {
                                    "type": "command",
                                    "name": "mkdir <dir>",
                                    "desc": "Créer un nouveau répertoire",
                                }
                            ]
                        },
                        {
                            "name": "story1",
                            "must_done": ["mkdir"],
                            "script": "quests.npc_def.Story1",
                            "desc": f"Vous semblez très talentueux. Vous devriez explorer la {forest[T]} et la {mountain[T]}, il y a des villageois qui pourraient avoir besoin de votre aide.",
                            "level": 0,
                            "rewards": [
                                {
                                    "type": "story",
                                    "value": "story1",
                                    "desc": f"Vous semblez très talentueux. Vous devriez explorer la {forest[T]} et la {mountain[T]}, il y a des villageois qui pourraient avoir besoin de votre aide.",
                                }
                            ],
                        }
                    ]
                },
                {
                    "name": "Quentintin",
                    "talk": f"Chut... Tu veux pas qu'on me remarque dans le {village[T]}, hein ?",
                    "quests":
                    [
                        {
                            "name": "Planque",
                            "must_done": ["mkdir", "list_hidden"],
                            "text": f"Je n'aime pas me retrouver au milieu du {village[T]}, cela m'angoisse, crée moi une planque par pitié",
                            "desc": f"Aide moi à créer un dossier caché planque pour me cacher dans le {village[T]} !",
                            "level": 1,
                            "script": "quests.npc_def.HiddenCreate"
                        },
                        {
                            "name": "Story5",
                            "must_done": ["Planque"],
                            "text": f"Va trouver le capitaine haddock près du {lake[T]}",
                            "desc": f"Trouver Haddock au {lake[T]}",
                            "level": 1,
                            "script": "quests.npc_def.Story5",
                            "rewards": [
                                {
                                    "type": "story",
                                    "value": "Story5",
                                    "desc": (
                                        f"Je me sens si bien, caché de tous !\n"
                                        f"Il parait qu'au fond du {lake[T]}, il y'a un trésor, si tu arrives à trouver le Capitaine Haddock, parle lui, il te conseillera"
                                    ),
                                }
                            ],
                        }
                    ]
                },
                {
                    "name": "Paul",
                    "talk": "Yo ! C'est moi, Paul, le roi des combines.",
                    "quests":
                    [
                        {
                            "name": "who_s_there",
                            "must_doing": ["fedex1"],
                            "text": f"Vous voulez des outils pour créer un tunnel à travers la {mountain[T]} ? Bien sûr, mais d'abord, vous devez me donner votre nom.",
                            "desc": "Donnez votre nom à Paul.",
                            "level": 1,
                            "script": "quests.npc_def.WhoIsThere",
                            "rewards": [
                                {
                                    "type": "command",
                                    "name": "sort <fichier> -o <fichier>",
                                    "desc": "Permet de trier les lignes d'un fichier par ordre alphabétique",
                                },
                            ]
                        },
                    ]
                }
            ]
        },
        {
            "name": mountain[T],
            "npcs":
            [
                {
                    "name": "Jacques",
                    "talk": f"Ouille... Ma jambe me fait souffrir, mais j'ai toujours le sourire !",
                    "quests":
                    [
                        {
                            "name": "move",
                            "must_done": [],
                            "text": f"J'ai une jambe cassée. S'il vous plaît, aidez-moi à retourner au {village[T]}.",
                            "desc": f"Aidez Jacques à retourner au {village[T]}.",
                            "level": 1,
                            "script": "quests.npc_def.Move",
                            "rewards":
                            [
                                {
                                    "type": "command",
                                    "name": "ls -a",
                                    "desc": "Lister tous les fichiers dans le répertoire courant, y compris les fichiers cachés",
                                },
                            ]
                        },
                        {
                            "name": "story2",
                            "must_done": ["move"],
                            "script": "quests.npc_def.Story2",
                            "desc": (
                                f"Merci de m'avoir aidé à retourner au {village[T]}.\n"
                                f"Je voulais aller de l'autre côté de la {mountain[T]}, mais je me suis cassé la jambe en essayant.\n"
                                f"Il était vraiment facile d'aller de l'autre côté de la {mountain[T]} il y a quelques semaines, mais le raccourci a été détruit avec le {village[T]}."
                            ),
                            "level": 0,
                            "rewards": [
                                {
                                    "type": "story",
                                    "value": "story2",
                                    "desc": (
                                        f"Merci de m'avoir aidé à retourner au {village[T]}.\n"
                                        f"Je voulais aller de l'autre côté de la {mountain[T]}, mais je me suis cassé la jambe en essayant.\n"
                                        f"Il était vraiment facile d'aller de l'autre côté de la {mountain[T]} il y a quelques semaines, mais le raccourci a été détruit avec le {village[T]}."
                                    ),
                                },
                                {
                                    "type": "command",
                                    "name": "mkdir .<dir>",
                                    "desc": "Créer un répertoire caché (commençant par un point)",
                                }
                            ]
                        }
                    ]
                }
            ],
            "subzones": [
                {
                    "name": translation_tab.secret_passage[T],  # .secret_passage
                    "must_done": ["list_hidden"],
                    "post_creation": lambda _: os.chmod(_, 0o600), # Must finishing the list_hidden quest to access this zone.
                    "npcs":
                    [
                        {
                            "name": "Ouvrier",
                            "talk": "Travail, boulot, sueur... Mais toujours avec le sourire !",
                            "quests":
                            [
                                {
                                    "name": "fedex1",
                                    "must_done": [],
                                    "text": f"Je veux que vous alliez au {village[T]} et que vous m'apportiez des outils pour faire un tunnel à travers la {mountain[T]}, demandez au villageois nommé Paul.npc.",
                                    "desc": f"Apportez des outils du {village[T]} au passage secret.",
                                    "level": 2,
                                    "script": "quests.npc_def.Fedex1",
                                    "setup_quest": "quests.npc_def.SetupFedex1",
                                    "rewards": [
                                        {
                                            "type": "command",
                                            "name": "whoami",
                                            "desc": "Afficher le nom de l'utilisateur actuel",
                                        },
                                    ]
                                },
                                {
                                    "name": "story3",
                                    "must_done": ["fedex1"],
                                    "script": "quests.npc_def.Story3",
                                    "desc": (
                                        f"Merci d'avoir apporté les outils !\n"
                                        f"Je peux maintenant creuser un tunnel à travers la {mountain[T]} jusqu'au {village[T]}.\n"
                                        f"Depuis que le raccourci a été détruit, il est vraiment difficile d'aller au {castle[T]}, beaucoup de villageois prennent des risques pour traverser la montagne."
                                    ),
                                    "level": 0,
                                    "rewards": [
                                        {
                                            "type": "story",
                                            "value": "story3",
                                            "desc": (
                                                f"Merci d'avoir apporté les outils !\n"
                                                f"Je peux maintenant creuser un tunnel à travers la {mountain[T]} jusqu'au {village[T]}.\n"
                                                f"Depuis que le raccourci a été détruit, il est vraiment difficile d'aller au {castle[T]}, beaucoup de villageois prennent des risques pour traverser la montagne."
                                            ),
                                        },
                                        {
                                            "type": "command",
                                            "name": "cp <source> <destination>",
                                            "desc": "Permet de copier un fichier",
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "subzones": [
                        {
                            "name": translation_tab.mountain_road[T],  # mountainroad
                            "post_creation": lambda _: os.chmod(_, 0o600), # Must finishing the fedex1 quest to access this zone. // FIXME: Permissions are reset after fedex1 quest 
                            "npcs":
                            [
                                {
                                    "name": "Marchand",
                                    "talk": "Bienvenue, voyageur ! Mes affaires sont aussi variées que mes histoires.",
                                    "quests":
                                    [
                                        {
                                            "name": "copy",
                                            "must_done": [],
                                            "text": "Une des roues de ma charrette est cassée, l'autre est en bon état. Pouvez-vous faire une copie de la bonne roue ?",
                                            "desc": "Aidez le marchand en copiant le contenu de la bonne roue.",
                                            "level": 2,
                                            "script": "quests.npc_def.Copy",
                                        },
                                        {
                                            "name": "story4",
                                            "must_done": ["copy"],
                                            "script": "quests.npc_def.Story4",
                                            "desc": (
                                                f"Merci d'avoir copié la bonne roue !\n"
                                                f"Vous avez aidé à construire le tunnel à travers la {mountain[T]} ? C'est génial ! "
                                                f"Vous devriez aller au {castle[T]}, le Roi pourrait chercher quelqu'un comme vous."
                                            ),
                                            "level": 0,
                                            "rewards": [
                                                {
                                                    "type": "story",
                                                    "value": "story4",
                                                    "desc": (
                                                        f"Merci d'avoir copié la bonne roue !\n"
                                                        f"Vous avez aidé à construire le tunnel à travers la {mountain[T]} ? C'est génial ! "
                                                        f"Vous devriez aller au {castle[T]}, le Roi pourrait chercher quelqu'un comme vous."
                                                    ),
                                                }
                                            ],
                                        }
                                    ]
                                }
                            ],
                            "objects": [
                                {
                                    "name": "roue",  # wheel
                                    "desc": "Une roue parfaitement fonctionnelle provenant de la charrette d'un marchand.",
                                    "content": "a312cb11576b058d0b9a13e1c06c61ac"
                                }
                            ],
                            "subzones": [
                                {
                                    "name": translation_tab.lake[T],  # lake
                                    "subzones": [
                                        {
                                            "name": translation_tab.sea[T],  # sea
                                            "symlink_to": f"{forest[T]}/{sea[T]}",  # forêt/mer (same beach as lac/mer)
                                        },
                                        {
                                            "name": translation_tab.lake_bottom[T],  # Fond du lac
                                            "npcs": [],
                                            "objects": create_lake_files()
                                        }
                                    ],
                                    "npcs": [
                                        {
                                            "name": "Haddock",
                                            "talk": "Nom d'un tonnerre ! Approche, moussaillon, et écoute bien !",
                                            "quests": [
                                                {
                                                "name": "Find treasure",
                                                "must_done": ["Planque"],
                                                "text": "Mille milliards de tonnerres de Brest ! Ramenez ce maudit trésor du fond du lac... au lac ! Pas à la cave, pas au grenier, au lac, triple buse !",
                                                "desc": "Ramenez le trésor pour le capitaine Haddock",
                                                "level": 2,
                                                "script": "quests.npc_def.Treasure"
                                                },
                                                {
                                                "name": "Open treasure",
                                                "must_done": ["Find treasure"],
                                                "text": "Mille sabords ! Voilà le trésor empaqueté dans ce maudit .tar !\n\n Pour l'ouvrir, bande de bachibouzouks, tapez donc : tar xvf tresor.tar \n...et que le butin se déverse enfin !",
                                                "desc": "Ramenez le trésor pour le capitaine Haddock",
                                                "level": 2,
                                                "script": "quests.npc_def.TreasureOpen"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "name": translation_tab.valley[T],  # valley
                                    "npcs": [],
                                    "objects": [],
                                    "subzones": [
                                        {
                                            "name": translation_tab.castle[T],  # castle
                                            "npcs": [
                                                {
                                                    "name": "Serviteur",
                                                    "talk": "Bienvenue au château, noble invité. Puis-je vous aider ?",
                                                    "quests": [
                                                        {
                                                            "name": "sort_books",
                                                            "must_done": [],
                                                            "text": "Désolé, mais je ne peux pas vous guider dans le château, je dois trier les livres dans la bibliothèque.",
                                                            "desc": "Trier les livres dans la bibliothèque du château.",
                                                            "level": 2,
                                                            "script": "quests.npc_def.SortBooks"
                                                        },
                                                        {
                                                            "name": "Is_king",
                                                            "must_done": ["brigands_phase2"],
                                                            "text": "Bravo vous avez tué les brigands ! Mais où est notre Roi ?",
                                                            "desc": "Le Roi est-il mort ?.",
                                                            "level": 2,
                                                            "script": "quests.npc_def.IsKing"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "subzones": [
                                                {
                                                    "name": translation_tab.library[T],  # library
                                                    "objects": [
                                                        {
                                                            "name": "livres",  # book
                                                            "desc": "Des livres qui doivent être trié.",
                                                            "content": "\n".join(livres) + "\n"
                                                        }
                                                    ],
                                                },
                                                {
                                                    "name": translation_tab.dungeon[T],  # dungeon
                                                    "npcs": [
                                                        {
                                                            "name": "Garde",
                                                            "talk": "Silence ! Je veille sur ce donjon, rien ne m'échappe.",
                                                            "quests": [
                                                                {
                                                                    "name": "shortcut",
                                                                    "must_done": ["sort_books"],
                                                                    "text": "J'ai besoin d'un raccourci vers le village, pouvez-vous en créer un ?",
                                                                    "desc": "Créer un raccourci vers le village.",
                                                                    "level": 3,
                                                                    "script": "quests.npc_def.Shortcut"
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                {
                                                    "name": translation_tab.throne_room[T],
                                                    "npcs": [
                                                            {
                                                                "name": "Roi",
                                                                "talk": "Approche, héros. Le royaume a besoin de ton courage.",
                                                                "quests": [
                                                                    {
                                                                        "name": "royal_summons",
                                                                        "must_done": [],
                                                                        "text": "Enfin, te voilà. Des brigands venu détruire le royaume vont arriver par la mer ! Il faut y remédier.",
                                                                        "desc": "Parler au Roi",
                                                                        "level": 0,
                                                                        "script": "quests.npc_def.KingSummons",
                                                                        "rewards": [
                                                                            {
                                                                                "type": "story",
                                                                                "value": "royal_summons",
                                                                                "desc": (
                                                                                    f"Je pars pour la {sea[T]}. Retrouve-moi là-bas, héros ! "
                                                                                    "Les brigands rôdent sur la plage..."
                                                                                ),
                                                                            }
                                                                        ],
                                                                    },
                                                                    {
                                                                        "name": "brigands_phase1",
                                                                        "must_done": ["royal_summons"],
                                                                        "text": "Élimine les 3 brigands sur la plage. Supprime-les un par un à la main.",
                                                                        "desc": "Vaincre 3 brigands manuellement.",
                                                                        "level": 2,
                                                                        "script": "quests.npc_def.KingBrigandsManual",
                                                                        "rewards": [
                                                                            {
                                                                                "type": "command",
                                                                                "name": "./canon.sh",
                                                                                "desc": "Faire tirer le canon"
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        "name": "brigands_phase2",
                                                                        "must_done": ["brigands_phase1"],
                                                                        "text": "Bien joué, mais ils reviennent par vagues ! Je te confie le canon.sh. Attention il peut s'avérer dangereux",
                                                                        "desc": "Vaincre tout les brigands",
                                                                        "level": 3,
                                                                        "script": "quests.npc_def.KingCanonIntro",
                                                                        "rewards": []
                                                                    },
                                                                    {
                                                                        "name": "brigands_phase3",
                                                                        "must_done": ["brigands_phase2"],
                                                                        "text": "Ils reviennent toujours. Trouve le processus chef_brigand et trouve un moyen de l'arrêter",
                                                                        "desc": "Vaincre le chef des brigands",
                                                                        "level": 4,
                                                                        "script": "quests.npc_def.KillProcess",
                                                                        "rewards": []
                                                                    }
                                                                ]
                                                            }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                }
            ],
        },
        {
            "name": translation_tab.forest[T],  # forest
            "npcs":
            [
                {
                    "name": "Alain_Leflou",
                    "talk": f"Oups, j'ai encore perdu mes lunettes... Tu peux m'aider ?",
                    "quests":
                    [
                        {
                            "must_done": [],
                            "name": "list_read",
                            "text": f"J'ai perdu mes lunettes, pouvez-vous lire le panneau pour moi afin que je puisse retourner au {village[T]} ?",
                            "desc": f"Lisez le panneau dans la {forest[T]}.",
                            "level": 1,
                            "script": "quests.npc_def.ReadFile",
                            "rewards":
                            [
                                {
                                    "type": "command",
                                    "name": "mv <source> <destination>",
                                    "desc": "Déplacer un fichier de la source à la destination",
                                },
                            ]
                        },
                        {
                            "must_done": ["list_read"],
                            "name": "list_hidden",
                            "text": f"Il y a une carte au trésor cachée dans la {forest[T]}.",
                            "desc": f"Trouvez et lisez le panneau caché dans la {forest[T]}.",
                            "level": 2,
                            "script": "quests.npc_def.HiddenFile",
                            "rewards":
                            [
                                {
                                    "type": "command",
                                    "name": "pwd",
                                    "desc": "Afficher le répertoire courant (le nom de la zone où vous vous trouvez actuellement)",
                                },
                            ]
                        }
                    ]
                },
            ],
            "objects":
            [
                {
                    "name": "panneau",  # sign
                    "desc": f"Un panneau en bois avec du texte dessus.",
                    "content": f"cd ../{village[T]}\n"
                },
                {
                    "name": ".carte_cachee",  # .hidden_sign
                    "desc": f"Une carte cachée avec du texte dessus.",
                    "content": f"cd ../{mountain[T]}/.passage_secret\n"
                }
            ],
            "subzones": [
                {
                    "name": translation_tab.sea[T],  # sea
                    "npcs": [
                        {
                            "name": "Pecheur",
                            "talk": "Le vent, les vagues... et mes histoires de coquillages !",
                            "quests": [
                                {
                                    "name": "collect_shells",
                                    "must_done": [],
                                    "text": "J'ai trouvé un joli coquillage, mais je n'en ai pas besoin. Je peux vous le donner si vous le voulez.",
                                    "desc": "Obtenez le joli coquillage du pêcheur.",
                                    "level": 1,
                                    "script": "quests.npc_def.AcceptShell",
                                    "rewards": [
                                        {
                                            "type": "command",
                                            "name": "whoami",
                                            "desc": "Afficher le nom de l'utilisateur actuel",
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                }
            ]
        }
    ],
}
