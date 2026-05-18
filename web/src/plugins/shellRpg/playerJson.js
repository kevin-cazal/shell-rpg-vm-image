/**
 * Guest pushes /tmp/player.json over hvc1 (vm-bridge-send / vm-bridge-raw xfer).
 * Host keeps the latest payload and shows level + quests in a popup.
 */
import { showPopup } from "../../popup/index.js";
import { isHvc1BridgeAttached, onHvc1Line } from "../../vmHVC1Bridge/index.js";

const SINGLE_PREFIX = "player.json ";
const XFER_BEGIN = "player.json xfer begin";
const XFER_CHUNK_PREFIX = "player.json xfer chunk ";
const XFER_END = "player.json xfer end";
const textDecoder = new TextDecoder("utf-8");

/** @param {...unknown} args */
function vmbLog(...args) {
  try {
    if (localStorage.getItem("VM_BRIDGE_DEBUG") === "0") return;
  } catch {
    /* ignore */
  }
  console.log("[vm-bridge][player.json]", ...args);
}

/** Latest guest /tmp/player.json (each bridge line replaces this). */
/** @type {object | null} */
let latestPlayerJson = null;

/** @type {boolean} */
let xferActive = false;
/** @type {string} */
let xferB64 = "";

function decodeBase64Utf8(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return textDecoder.decode(bytes);
}

function applyPlayerJsonFromGuest(b64) {
  if (!b64) return;
  try {
    latestPlayerJson = JSON.parse(decodeBase64Utf8(b64));
    vmbLog(`updated from guest b64_len=${b64.length}`);
    window.dispatchEvent(
      new CustomEvent("shellRpg:playerJson", { detail: latestPlayerJson }),
    );
  } catch (err) {
    vmbLog(`parse failed b64_len=${b64.length}`, err);
    console.warn("[shellRpg] player.json push parse failed:", err);
  }
}

function resetXfer() {
  xferActive = false;
  xferB64 = "";
}

function ingestPlayerJsonLine(line) {
  if (line === XFER_BEGIN) {
    vmbLog("xfer begin");
    xferActive = true;
    xferB64 = "";
    return;
  }

  if (line.startsWith(XFER_CHUNK_PREFIX)) {
    const piece = line.slice(XFER_CHUNK_PREFIX.length);
    if (!xferActive) {
      xferActive = true;
      xferB64 = "";
    }
    xferB64 += piece;
    return;
  }

  if (line === XFER_END) {
    const payload = xferB64;
    resetXfer();
    applyPlayerJsonFromGuest(payload);
    return;
  }

  if (
    line.startsWith(SINGLE_PREFIX) &&
    !line.startsWith("player.json xfer")
  ) {
    applyPlayerJsonFromGuest(line.slice(SINGLE_PREFIX.length));
  }
}

/** @returns {object | null} */
export function getPlayerJson() {
  return latestPlayerJson;
}

export function registerPlayerJsonBridge() {
  onHvc1Line(ingestPlayerJsonLine);
}

/** Total gained level (same field as engine save: sum of completed quest levels). */
/** @param {object} data */
function playerLevel(data) {
  if (typeof data.level === "number") {
    return data.level;
  }
  const done = Array.isArray(data.quests_done) ? data.quests_done : [];
  return done.reduce((sum, q) => sum + (Number(q?.level) || 0), 0);
}

/** Quests with level > 0 (in-game filter). */
/** @param {unknown} quests */
function questsWithLevel(quests) {
  if (!Array.isArray(quests)) return [];
  return quests.filter(
    (q) => q && typeof q === "object" && (Number(q.level) || 0) > 0,
  );
}

/** @param {HTMLElement} parent */
/** @param {string} title */
/** @param {(body: HTMLElement) => boolean} buildBody */
function appendSection(parent, title, buildBody) {
  const section = document.createElement("section");
  section.className = "player-state-section";

  const heading = document.createElement("h3");
  heading.className = "player-state-section-title";
  heading.textContent = title;
  section.append(heading);

  const body = document.createElement("div");
  body.className = "player-state-section-body";
  const hasContent = buildBody(body);
  if (!hasContent) {
    const empty = document.createElement("p");
    empty.className = "player-state-empty";
    empty.textContent = "None";
    body.append(empty);
  }

  section.append(body);
  parent.append(section);
}

/** @param {HTMLElement} listEl */
/** @param {{ name: string, level: number, desc: string }[]} items */
function fillQuestList(listEl, items) {
  for (const item of items) {
    const li = document.createElement("li");
    li.className = "player-state-quest";

    const head = document.createElement("div");
    head.className = "player-state-quest-head";

    const name = document.createElement("span");
    name.className = "player-state-quest-name";
    name.textContent = item.name;

    const level = document.createElement("span");
    level.className = "player-state-quest-level";
    level.textContent = `Lv ${item.level}`;

    head.append(name, level);
    li.append(head);

    if (item.desc) {
      const desc = document.createElement("p");
      desc.className = "player-state-quest-desc";
      desc.textContent = item.desc;
      li.append(desc);
    }

    listEl.append(li);
  }
}

/** @param {object} q */
function questRow(q) {
  return {
    name: typeof q.name === "string" ? q.name : "?",
    level: Number(q.level) || 0,
    desc: typeof q.desc === "string" ? q.desc.trim() : "",
  };
}

/** @param {HTMLElement} container */
/** @param {object} data */
function renderPlayerStateView(container, data) {
  const root = document.createElement("div");
  root.className = "player-state-view";

  const hero = document.createElement("div");
  hero.className = "player-state-hero";

  const levelBlock = document.createElement("div");
  levelBlock.className = "player-state-level";
  const levelValue = document.createElement("span");
  levelValue.className = "player-state-level-value";
  levelValue.textContent = String(playerLevel(data));
  const levelLabel = document.createElement("span");
  levelLabel.className = "player-state-level-label";
  levelLabel.textContent = "Level";
  levelBlock.append(levelValue, levelLabel);
  hero.append(levelBlock);

  root.append(hero);

  const active = questsWithLevel(data.quests).map(questRow);
  appendSection(root, "Active quests", (body) => {
    if (!active.length) return false;
    const list = document.createElement("ul");
    list.className = "player-state-quest-list";
    fillQuestList(list, active);
    body.append(list);
    return true;
  });

  const done = questsWithLevel(data.quests_done).map(questRow);
  appendSection(root, "Completed quests", (body) => {
    if (!done.length) return false;
    const list = document.createElement("ul");
    list.className = "player-state-quest-list";
    fillQuestList(list, done);
    body.append(list);
    return true;
  });

  container.append(root);
}

/** @param {object} data */
function showPlayerJsonPopup(data) {
  showPopup({
    title: "Player state",
    render(container) {
      renderPlayerStateView(container, data);
    },
  });
}

/** @param {string} message */
function showPlayerJsonMessage(message) {
  showPopup({
    title: "Player state",
    render(container) {
      const p = document.createElement("p");
      p.className = "player-state-empty";
      p.textContent = message;
      container.append(p);
    },
  });
}

/** @returns {import("../../menu/index.js").MenuItem[]} */
export function getPlayerJsonMenuItems() {
  return [
    {
      type: "action",
      label: "View player state…",
      disabled: () => !isHvc1BridgeAttached(),
      onClick() {
        const data = getPlayerJson();
        if (data) {
          showPlayerJsonPopup(data);
          return;
        }
        showPlayerJsonMessage(
          "No player state received yet from the guest. Progress in-game or run vm-bridge-player-json.sh.",
        );
      },
    },
  ];
}
