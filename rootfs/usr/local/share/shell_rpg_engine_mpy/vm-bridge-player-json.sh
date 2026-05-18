#!/bin/sh
# Push /tmp/player.json to the web host on /dev/hvc1.
# Small file: one line via vm-bridge-send (player.json <base64>).
# Large file: xfer lines in one vm-bridge-raw write (avoids losing middle packets).

# Set VM_BRIDGE_DEBUG=0 to silence guest xfer tracing.
: "${VM_BRIDGE_DEBUG:=1}"
export VM_BRIDGE_DEBUG

vmb_log() {
	[ "$VM_BRIDGE_DEBUG" != 0 ] || return 0
	printf '[vm-bridge-player-json] %s\n' "$*" >&2
}

_SINGLE_MAX_B64=4000
_CHUNK_WIDTH=3500
_LINE_MAX=4096
_CHUNK_PREFIX='player.json xfer chunk '
_CHUNK_PREFIX_LEN=23

[ -r /tmp/player.json ] || exit 0
[ -w /dev/hvc1 ] || exit 0

_b64=$(base64 /tmp/player.json 2>/dev/null | tr -d '\n') || exit 0
[ -n "$_b64" ] || exit 0

# Fits in one vm-bridge-send line (LINE_MAX 4096).
if [ "${#_b64}" -le "$_SINGLE_MAX_B64" ]; then
	vmb_log "single-line push b64_len=${#_b64}"
	exec /usr/local/bin/vm-bridge-send "player.json $_b64"
fi

_chunks=/tmp/.player-json-b64.chunks.$$
_xfer=/tmp/.player-json-xfer.$$
printf '%s' "$_b64" | fold -w "$_CHUNK_WIDTH" >"$_chunks" || exit 1
_chunk_count=$(wc -l <"$_chunks" | tr -d ' ')
vmb_log "xfer begin b64_len=${#_b64} chunk_width=$_CHUNK_WIDTH chunk_count=$_chunk_count"

{
	printf '%s\n' 'player.json xfer begin'
	_chunk_i=0
	while IFS= read -r _c; do
		[ -n "$_c" ] || continue
		if [ $((${#_c} + _CHUNK_PREFIX_LEN)) -ge "$_LINE_MAX" ]; then
			vmb_log "xfer abort: chunk $_chunk_i line too long (${#_c}+$_CHUNK_PREFIX_LEN)"
			exit 1
		fi
		_chunk_i=$((_chunk_i + 1))
		vmb_log "xfer chunk $_chunk_i/${_chunk_count} payload_len=${#_c} line_len=$((${#_c} + _CHUNK_PREFIX_LEN))"
		printf '%s%s\n' "$_CHUNK_PREFIX" "$_c"
	done <"$_chunks"
	printf '%s\n' 'player.json xfer end'
} >"$_xfer" || {
	rm -f "$_chunks" "$_xfer"
	exit 1
}
_xfer_bytes=$(wc -c <"$_xfer" | tr -d ' ')
_xfer_lines=$(wc -l <"$_xfer" | tr -d ' ')
rm -f "$_chunks"
vmb_log "xfer file $_xfer bytes=$_xfer_bytes lines=$_xfer_lines chunks_emitted=$_chunk_i"

/usr/local/bin/vm-bridge-raw "$_xfer" || {
	vmb_log "vm-bridge-raw failed"
	rm -f "$_xfer"
	exit 1
}
vmb_log "xfer end ok"
rm -f "$_xfer"
