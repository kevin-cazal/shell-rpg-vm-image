/**
 * Shell RPG plugin: zone backgrounds + player.json via /dev/hvc1.
 * Loaded via main.js side effect; app.js stays generic.
 */
import { registerPluginMenu } from "../menu/index.js";
import {
  getPlayerJsonMenuItems,
  registerPlayerJsonBridge,
} from "./shellRpg/playerJson.js";
import {
  getZoneBackgroundMenuItems,
  registerZoneBackground,
} from "./shellRpg/zoneBackground.js";

registerZoneBackground();
registerPlayerJsonBridge();

registerPluginMenu("shellRpg", "shellRpg", () => [
  ...getZoneBackgroundMenuItems(),
  ...getPlayerJsonMenuItems(),
]);
