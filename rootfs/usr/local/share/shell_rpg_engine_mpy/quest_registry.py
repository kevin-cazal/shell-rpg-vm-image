import compat  # noqa: F401

import npc_def as nd

QUEST_SCRIPTS = {
    "quests.npc_def.Mkdir": nd.Mkdir,
    "quests.npc_def.HiddenCreate": nd.HiddenCreate,
    "quests.npc_def.Treasure": nd.Treasure,
    "quests.npc_def.TreasureOpen": nd.TreasureOpen,
    "quests.npc_def.ReadFile": nd.ReadFile,
    "quests.npc_def.WhoIsThere": nd.WhoIsThere,
    "quests.npc_def.Move": nd.Move,
    "quests.npc_def.Fedex1": nd.Fedex1,
    "quests.npc_def.Copy": nd.Copy,
    "quests.npc_def.SortBooks": nd.SortBooks,
    "quests.npc_def.Shortcut": nd.Shortcut,
    "quests.npc_def.HiddenFile": nd.HiddenFile,
    "quests.npc_def.AlwaysValid": nd.AlwaysValid,
    "quests.npc_def.AcceptShell": nd.AcceptShell,
    "quests.npc_def.KingSummons": nd.KingSummons,
    "quests.npc_def.KingBrigandsManual": nd.KingBrigandsManual,
    "quests.npc_def.KingCanonIntro": nd.KingCanonIntro,
    "quests.npc_def.KillProcess": nd.KillProcess,
    "quests.npc_def.IsKing": nd.IsKing,
    "quests.npc_def.Story1": nd.Story1,
    "quests.npc_def.Story2": nd.Story2,
    "quests.npc_def.Story3": nd.Story3,
    "quests.npc_def.Story4": nd.Story4,
    "quests.npc_def.Story5": nd.Story5,
}


def resolve(script_name):
    return QUEST_SCRIPTS.get(script_name)
