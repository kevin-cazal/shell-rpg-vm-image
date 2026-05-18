/**
 * Shell RPG: terminal host backgrounds driven by hvc1 "bg …" lines.
 */
import { showPopup } from "../../popup/index.js";
import { onHvc1Line } from "../../vmHVC1Bridge/index.js";

const TERMINAL_HOST_ID = "terminal";
const ZONE_BG_STORAGE_KEY = "shellRpg.zoneBackground";

/** @type {ReturnType<typeof createZoneBackgroundController> | null} */
let zoneBackground = null;

let zoneBackgroundEnabled = true;

try {
  const stored = localStorage.getItem(ZONE_BG_STORAGE_KEY);
  if (stored === "0") zoneBackgroundEnabled = false;
  else if (stored === "1") zoneBackgroundEnabled = true;
} catch {
  /* ignore */
}

function terminalHost() {
  return document.getElementById(TERMINAL_HOST_ID);
}

function clearZoneBackground() {
  zoneBackground?.clear();
  zoneBackground = null;
  const hostEl = terminalHost();
  if (hostEl) {
    hostEl.classList.remove("terminal-has-bg");
    hostEl.style.removeProperty("--zone-bg-image");
  }
}

function ensureZoneBackground() {
  const hostEl = terminalHost();
  if (!hostEl) return null;
  if (!zoneBackground) {
    zoneBackground = createZoneBackgroundController(null, { hostEl });
  }
  return zoneBackground;
}

/**
 * @param {import("@xterm/xterm").Terminal | null} terminal
 * @param {{ baseUrl?: string, hostEl?: HTMLElement }} [options]
 */
export function createZoneBackgroundController(terminal, options = {}) {
  const baseUrl = options.baseUrl ?? "/bg/";
  const hostEl = options.hostEl ?? terminal?.element?.parentElement;

  const apply = (filename) => {
    if (!hostEl) return;
    const url = `${baseUrl}${encodeURIComponent(filename)}`;
    hostEl.classList.add("terminal-has-bg");
    hostEl.style.setProperty("--zone-bg-image", `url("${url}")`);
  };

  const clear = () => {
    if (!hostEl) return;
    hostEl.classList.remove("terminal-has-bg");
    hostEl.style.removeProperty("--zone-bg-image");
  };

  const handleBridgeLine = (line) => {
    if (!line.startsWith("bg ")) return;
    const arg = line.slice(3).trim();
    if (!arg || arg === "clear") {
      clear();
      return;
    }
    apply(arg);
  };

  return { apply, clear, handleBridgeLine };
}

export function registerZoneBackground() {
  onHvc1Line((line) => {
    if (!zoneBackgroundEnabled) return;
    ensureZoneBackground()?.handleBridgeLine(line);
  });

  window.addEventListener("vm-terminal-dispose", () => {
    clearZoneBackground();
  });
}

/** @returns {import("../../menu/index.js").MenuItem[]} */
export function getZoneBackgroundMenuItems() {
  return [
    {
      type: "action",
      label: "About zone backgrounds…",
      onClick() {
        showPopup({
          title: "Zone backgrounds",
          render(container) {
            const p = document.createElement("p");
            p.textContent =
              "When the guest prints a line starting with bg on /dev/hvc1, the terminal background switches to that zone image.";
            container.append(p);
          },
        });
      },
    },
    {
      type: "checkbox",
      label: "Zone backgrounds",
      getChecked: () => zoneBackgroundEnabled,
      onChange(checked) {
        zoneBackgroundEnabled = checked;
        try {
          localStorage.setItem(ZONE_BG_STORAGE_KEY, checked ? "1" : "0");
        } catch {
          /* ignore */
        }
        if (!checked) clearZoneBackground();
      },
    },
  ];
}
