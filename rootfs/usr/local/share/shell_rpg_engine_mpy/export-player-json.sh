#!/bin/sh
# Export /tmp/player.json to /mnt/host/player.json for the browser menu (host9p).
# Remounts host9p first so resume/reload reconnects to the fresh host VFS.

_FALLBACK='Lisez directement /tmp/player.json dans le terminal.'

[ -r /tmp/player.json ] || {
	printf '%s\n' "export-player-json: /tmp/player.json introuvable. $_FALLBACK" >&2
	exit 1
}

if ! /usr/local/sbin/mount-host-share; then
	printf '%s\n' "export-player-json: impossible de monter host9p (/mnt/host). $_FALLBACK" >&2
	exit 1
fi

if ! cp /tmp/player.json /mnt/host/player.json; then
	printf '%s\n' "export-player-json: copie vers /mnt/host/player.json echouee. $_FALLBACK" >&2
	exit 1
fi

exit 0
