import os

_COLS_TMP = "/tmp/.rpg_cols"
_ROWS_TMP = "/tmp/.rpg_rows"
_PAGER_TMP = "/tmp/.rpg_pager.txt"
_RPG_TTY_FILE = "/tmp/.rpg_tty"
_RPG_INJECT_CMD_FILE = "/tmp/.rpg_inject_cmd"
_RPG_INJECT_BIN = "/usr/local/bin/rpg-inject-tty"
# No -S: chopping pre-sized Unicode box lines splits UTF-8 (broken │/┐ on the right).
_DEFAULT_PAGER = "less -E -R"
_DEFAULT_COLS = 80
_MIN_DETECTED = 28
_MIN_BOX_WIDTH = 32
_MAX_BOX_WIDTH = 78
# Leave unused tty columns so Unicode borders stay inside the viewport when the
# host over-reports width (browser zoom + xterm fit rounding on virtio hvc0).
_DEFAULT_BOX_COL_MARGIN = 2

_NOTIFY_HEADERS = {
    "quest_new": "NOUVELLE QUÊTE",
    "quest_done": "QUÊTE TERMINÉE",
    "reward_command": "RÉCOMPENSE",
    "reward_story": "LORE",
    "system": "",
}

# Unicode icons (unicode box mode; mlterm --emoji=Twemoji.ttf)
_SYM_PERSON = "\U0001f464"   # NPC
_SYM_QUEST = "\U0001f3af"    # quest / objective
_SYM_TROPHY = "\U0001f3c6"   # reward
_SYM_BOOK = "\U0001f4d6"     # story / lore
_SYM_PLAYER = "\U0001f3ae"   # player sheet
_SYM_LEVEL = "\U0001f530"    # 🔰 level
_SYM_COMMAND = "\U0001f680"  # 🚀 commands
_SYM_DONE = "\U0001f3c1"     # 🏁 completed (mlterm/Twemoji; checks U+2705/U+1F7E2 missing)
_SYM_SYSTEM = "\U0001f537"   # 🔷 system / info

# Supplementary-plane symbols used in box headers (player sheet, sections).
_UI_HEADER_SYMBOLS = (
    _SYM_PLAYER,
    _SYM_PERSON,
    _SYM_QUEST,
    _SYM_TROPHY,
    _SYM_BOOK,
    _SYM_LEVEL,
    _SYM_COMMAND,
    _SYM_DONE,
    _SYM_SYSTEM,
)

_NOTIFY_SYMBOLS = {
    "quest_new": _SYM_QUEST,
    "quest_done": _SYM_QUEST,
    "reward_command": _SYM_TROPHY,
    "reward_story": _SYM_BOOK,
    "system": _SYM_SYSTEM,
}

# Light box (U+250x) for NPC dialogue
_UNICODE_NPC = {
    "top_prefix": "\u250c\u2500 ",   # ┌─
    "top_fill": "\u2500",            # ─
    "top_end": "\u2510",             # ┐
    "body_left": "\u2502 ",          # │
    "body_right": " \u2502",         # │
    "bottom_left": "\u2514",         # └
    "bottom_fill": "\u2500",         # ─
    "bottom_right": "\u2518",        # ┘
}

# Double box (U+255x) for engine notifications
_UNICODE_NOTIFY = {
    "top_prefix": "\u2554\u2550",    # ╔═
    "top_fill": "\u2550",            # ═
    "top_end": "\u2557",             # ╗
    "body_left": "\u2551 ",          # ║
    "body_right": " \u2551",         # ║
    "bottom_left": "\u255a",         # ╚
    "bottom_fill": "\u2550",         # ═
    "bottom_right": "\u255d",        # ╝
}

_ASCII_NPC = {
    "top_prefix": "+-- ",
    "top_fill": "-",
    "top_end": "+",
    "body_left": "| ",
    "body_right": " |",
    "bottom_left": "+",
    "bottom_fill": "-",
    "bottom_right": "+",
}

_ASCII_NOTIFY = {
    "top_prefix": "+==",
    "top_fill": "=",
    "top_end": "+",
    "body_left": "| ",
    "body_right": " |",
    "bottom_left": "+",
    "bottom_fill": "=",
    "bottom_right": "+",
}

_use_unicode_cache = None


def bold(text):
    return "\033[1m" + text + "\033[0m"


def _shell_quote(s):
    return "'" + str(s).replace("'", "'\"'\"'") + "'"


def inject_shell_input(text):
    """Inject keystrokes into the player's shell tty (TIOCSTI; see rpg-inject-tty)."""
    try:
        with open(_RPG_TTY_FILE, "r") as f:
            tty = f.read().strip()
    except OSError:
        return
    if not tty:
        return
    payload = str(text)
    if not payload.endswith("\n"):
        payload += "\n"
    try:
        with open(_RPG_INJECT_CMD_FILE, "w") as f:
            f.write(payload)
    except OSError:
        return
    os.system(
        _RPG_INJECT_BIN
        + " "
        + _shell_quote(tty)
        + " < "
        + _RPG_INJECT_CMD_FILE
    )


def request_cd(path):
    """Queue cd in the player shell after talk returns (fedex1 → montagne)."""
    inject_shell_input("cd " + str(path))


def strip_ansi(text):
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "\033":
            j = i + 1
            if j < n and text[j] == "[":
                j += 1
                while j < n and text[j] not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
                    j += 1
                if j < n:
                    j += 1
            i = j
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


try:
    import unicodedata as _unicodedata
except ImportError:
    _unicodedata = None


def _is_wide_emoji_codepoint(o):
    # Supplemental emoji and symbols (exclude U+2500–U+257F box drawing).
    if 0x1F300 <= o <= 0x1FAFF:
        return True
    if 0x1F1E6 <= o <= 0x1F1FF:
        return True
    if 0x2600 <= o <= 0x27BF:
        return True
    if 0x2B05 <= o <= 0x2B55:
        return True
    if 0x3030 <= o <= 0x303D:
        return True
    if 0x3297 <= o <= 0x3299:
        return True
    return False


def _glyph_width(ch):
    o = ord(ch)
    if o < 32 or o == 127:
        return 0
    if o in (0xFE0E, 0xFE0F) or o == 0x200D:
        return 0
    # Web/xterm (hvc0): game UI emoji render in one cell with the bundled mono font.
    if _is_scrollback_console():
        for sym in _UI_HEADER_SYMBOLS:
            if ch in sym:
                return 1
    if _unicodedata is not None:
        cat = _unicodedata.category(ch)
        if cat in ("Mn", "Me"):
            return 0
        eaw = _unicodedata.east_asian_width(ch)
        if eaw in ("W", "F"):
            return 2
        if eaw == "A" and _is_wide_emoji_codepoint(o):
            return 2
        if cat == "Cf" and o != 0x200D:
            return 0
        return 1
    if _is_wide_emoji_codepoint(o):
        return 2
    if 0x1100 <= o <= 0x115F:
        return 2
    if 0x2329 <= o <= 0x232A:
        return 2
    if 0x2E80 <= o <= 0xA4CF:
        return 2
    if 0xAC00 <= o <= 0xD7A3:
        return 2
    if 0xF900 <= o <= 0xFAFF:
        return 2
    if 0xFE10 <= o <= 0xFE19:
        return 2
    if 0xFE30 <= o <= 0xFE6F:
        return 2
    if 0xFF00 <= o <= 0xFF60:
        return 2
    if 0xFFE0 <= o <= 0xFFE6:
        return 2
    return 1


def visible_len(text):
    width = 0
    for ch in strip_ansi(text):
        width += _glyph_width(ch)
    return width


def _truncate_to_visible(text, max_width):
    if max_width <= 0:
        return ""
    if visible_len(text) <= max_width:
        return text
    out = []
    w = 0
    for ch in text:
        cw = _glyph_width(ch)
        if w + cw > max_width:
            break
        out.append(ch)
        w += cw
    return "".join(out)


def _getenv(name):
    try:
        return os.getenv(name)
    except AttributeError:
        return None


def _locale_utf8():
    for var in ("LC_ALL", "LC_CTYPE", "LANG"):
        val = _getenv(var)
        if val:
            upper = val.upper()
            if "UTF-8" in upper or "UTF8" in upper:
                return True
    return False


def _term_supports_unicode():
    term = (_getenv("TERM") or "").lower()
    if not term:
        return False
    markers = ("rxvt", "urxvt", "mlterm", "unicode", "xterm", "konsole", "alacritty", "kitty", "foot", "wezterm")
    for marker in markers:
        if marker in term:
            return True
    return False


def use_unicode_boxes():
    global _use_unicode_cache
    if _use_unicode_cache is not None:
        return _use_unicode_cache
    if _getenv("RPG_UI_ASCII") == "1":
        _use_unicode_cache = False
        return False
    if _getenv("RPG_UI_UNICODE") == "1":
        _use_unicode_cache = True
        return True
    _use_unicode_cache = _term_supports_unicode() and _locale_utf8()
    return _use_unicode_cache


def _charset(style, for_pager=False):
    if for_pager:
        if style == "npc":
            return _ASCII_NPC
        return _ASCII_NOTIFY
    if use_unicode_boxes():
        if style == "npc":
            return _UNICODE_NPC
        return _UNICODE_NOTIFY
    if style == "npc":
        return _ASCII_NPC
    return _ASCII_NOTIFY


def _read_stty_cols():
    os.system("stty size 2>/dev/null | awk '{print $2}' > " + _COLS_TMP)
    try:
        with open(_COLS_TMP, "r") as f:
            value = f.read().strip()
        if value:
            return int(value)
    except (OSError, ValueError):
        pass
    return 0


def _read_stty_rows():
    os.system("stty size 2>/dev/null | awk '{print $1}' > " + _ROWS_TMP)
    try:
        with open(_ROWS_TMP, "r") as f:
            value = f.read().strip()
        if value:
            return int(value)
    except (OSError, ValueError):
        pass
    return 0


def terminal_cols():
    # Kernel/winsize (stty) reflects virtio resize; COLUMNS may be stale in the shell.
    cols = _read_stty_cols()
    if cols > 0:
        return cols
    cols_str = _getenv("COLUMNS")
    if cols_str:
        try:
            cols = int(cols_str)
            if cols > 0:
                return cols
        except ValueError:
            pass
    return _DEFAULT_COLS


def terminal_rows():
    rows = _read_stty_rows()
    if rows > 0:
        return rows
    return 24


def _box_col_margin():
    env = _getenv("RPG_BOX_COL_MARGIN")
    if env is not None:
        try:
            return max(0, int(env))
        except ValueError:
            pass
    return _DEFAULT_BOX_COL_MARGIN


def _box_width():
    detected = terminal_cols()
    margin = _box_col_margin()
    usable = detected - margin if detected > margin else detected
    return max(_MIN_BOX_WIDTH, min(usable, _MAX_BOX_WIDTH))


def _outer_width_for_box(header_text, for_pager=False):
    return _box_width()


def _display_name(speaker):
    if speaker.endswith(".npc"):
        return speaker[:-4]
    return speaker


def _npc_header_title(display_name):
    if use_unicode_boxes():
        return _SYM_PERSON + " " + display_name
    return display_name


def _notify_header_text(kind, base_header):
    sym = _NOTIFY_SYMBOLS.get(kind, "")
    if sym and use_unicode_boxes():
        if base_header:
            return sym + " " + base_header
        return sym
    return base_header


def _player_main_header(for_pager=False):
    title = "FICHE JOUEUR"
    if for_pager or not use_unicode_boxes():
        return title
    return _SYM_PLAYER + " " + title


def format_level_line(level, for_pager=False):
    line = "Niveau: " + str(level)
    if for_pager or not use_unicode_boxes():
        return line
    return _SYM_LEVEL + " " + line


def _player_section_header(section_kind, title, for_pager=False):
    if for_pager or not use_unicode_boxes():
        return title
    symbols = {
        "quests_active": _SYM_QUEST,
        "quests_done": _SYM_DONE,
        "commands": _SYM_COMMAND,
        "stories": _SYM_BOOK,
    }
    sym = symbols.get(section_kind, "")
    if sym:
        return sym + " " + title
    return title


def _strip_ui_symbols(line):
    for sym in (_SYM_LEVEL, _SYM_QUEST, _SYM_DONE, _SYM_COMMAND, _SYM_BOOK, _SYM_PLAYER):
        prefix = sym + " "
        if line.startswith(prefix):
            return line[len(prefix):]
    return line


def _pager_hint_lines(ascii_only=False):
    rule_len = max(28, min(terminal_cols() - 4, 60))
    if ascii_only or not use_unicode_boxes():
        rule = "-" * rule_len
        hint = "  Q pour quitter  |  Espace : page suivante  |  B : page precedente"
    else:
        rule = "\u2500" * rule_len
        hint = "  Q pour quitter  \u00b7  Espace : page suivante  \u00b7  B : page pr\u00e9c\u00e9dente"
    return [rule, hint, rule]


def _pager_cmd():
    return _getenv("RPG_PAGER") or _DEFAULT_PAGER


def _pager_use_ascii():
    if _getenv("RPG_UI_PAGER_ASCII") == "1":
        return True
    return not use_unicode_boxes()


def _is_scrollback_console():
    """Virtio/serial consoles used by the web runner and QEMU (xterm scrollback)."""
    if _getenv("RPG_NO_PAGER") == "1":
        return True
    try:
        with open(_RPG_TTY_FILE, "r") as f:
            tty = f.read().strip()
    except OSError:
        tty = ""
    return tty in ("/dev/hvc0", "/dev/ttyS0")


def _needs_external_pager(text):
    if _is_scrollback_console():
        return False
    hint_lines = len(_pager_hint_lines(ascii_only=_pager_use_ascii())) + 2
    rows = terminal_rows()
    return _count_lines(text) + hint_lines > max(rows - 1, 12)


def _count_lines(text):
    if not text:
        return 0
    return text.count("\n") + 1


def _run_external_pager(path, unicode_pager=False):
    # Default pager: less -E -R (exit at EOF, ANSI; lines are pre-sized to terminal cols).
    cols = terminal_cols()
    env_parts = []
    if cols > 0:
        env_parts.append("COLUMNS=" + str(cols))
    if unicode_pager:
        env_parts.append("LESSCHARSET=utf-8")
    cols_env = " ".join(env_parts)
    if cols_env:
        cols_env += " "
    cmds = [cols_env + _pager_cmd() + " " + path]
    if not unicode_pager:
        cmds.append(cols_env + "busybox " + _DEFAULT_PAGER + " " + path)
    cmds.append("more -d " + path)
    for cmd in cmds:
        try:
            if os.system(cmd) == 0:
                return True
        except OSError:
            continue
    return False


def pager_show(text, ascii_pager=None):
    text = str(text).rstrip()
    if ascii_pager is None:
        ascii_pager = _pager_use_ascii()
    if _is_scrollback_console() or (not ascii_pager and not _needs_external_pager(text)):
        print(text)
        return
    hint_block = "\n".join(_pager_hint_lines(ascii_only=ascii_pager))
    full = text + "\n\n" + hint_block
    try:
        with open(_PAGER_TMP, "w") as f:
            f.write(full)
            if not full.endswith("\n"):
                f.write("\n")
    except OSError:
        print(full)
        return
    _run_external_pager(_PAGER_TMP, unicode_pager=not ascii_pager)


def _wrap_body_lines(lines, inner_width):
    wrapped = []
    for line in lines:
        text = str(line)
        if visible_len(text) <= inner_width:
            wrapped.append(text)
        else:
            wrapped.extend(wrap_text(text, inner_width))
    return wrapped if wrapped else [""]


def _split_word_by_width(word, width):
    if width <= 0:
        return [word]
    parts = []
    chunk = ""
    chunk_w = 0
    for ch in word:
        cw = _glyph_width(ch)
        if chunk and chunk_w + cw > width:
            parts.append(chunk)
            chunk = ch
            chunk_w = cw
        else:
            chunk += ch
            chunk_w += cw
    if chunk:
        parts.append(chunk)
    return parts if parts else [""]


def _wrap_paragraph(paragraph, width):
    paragraph = paragraph.strip()
    if not paragraph:
        return [""]
    words = paragraph.split()
    lines = []
    current = []
    current_len = 0
    for word in words:
        wlen = visible_len(word)
        if wlen > width:
            if current:
                lines.append(" ".join(current))
                current = []
                current_len = 0
            for part in _split_word_by_width(word, width):
                lines.append(part)
            continue
        if current and current_len + 1 + wlen > width:
            lines.append(" ".join(current))
            current = [word]
            current_len = wlen
        else:
            if current:
                current_len += 1 + wlen
            else:
                current_len = wlen
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines if lines else [""]


def wrap_text(text, width):
    lines = []
    for paragraph in text.split("\n"):
        lines.extend(_wrap_paragraph(paragraph, width))
    return lines


def _pad_line(line, width):
    line = _truncate_to_visible(line, width)
    pad = width - visible_len(line)
    if pad > 0:
        return line + (" " * pad)
    return line


def _fit_header_label(label, max_width):
    if max_width <= 0:
        return ""
    if visible_len(label) <= max_width:
        return label
    if max_width <= 3:
        out = ""
        w = 0
        for ch in label:
            cw = _glyph_width(ch)
            if w + cw > max_width:
                break
            out += ch
            w += cw
        return out
    target = max_width - 3
    out = ""
    w = 0
    for ch in label:
        cw = _glyph_width(ch)
        if w + cw > target:
            break
        out += ch
        w += cw
    return out + "..."


def _repeat_char(ch, count):
    if count <= 0:
        return ""
    return ch * count


def _top_border_labeled(title_text, outer_width, cs, with_person=False, for_pager=False):
    prefix = cs["top_prefix"]
    title = _npc_header_title(title_text) if with_person else title_text
    # No ANSI on border lines: SGR sequences must not affect serial/web width.
    label = title
    label_vis = visible_len(title)
    end = cs["top_end"]
    fill_len = outer_width - visible_len(prefix) - visible_len(end) - label_vis
    if fill_len < 0:
        fill_len = 0
    return prefix + label + _repeat_char(cs["top_fill"], fill_len) + end


def _top_border_npc(display_name, outer_width, cs):
    return _top_border_labeled(display_name, outer_width, cs, with_person=True)


def _top_border_notify(header_label, outer_width, cs):
    if header_label:
        inner = "[ " + header_label + " ]"
    else:
        inner = "[ ]"
    prefix = cs["top_prefix"]
    end = cs["top_end"]
    inner_len = visible_len(inner)
    fill_len = outer_width - visible_len(prefix) - visible_len(end) - inner_len
    if fill_len < 0:
        max_label = outer_width - visible_len(prefix) - visible_len(end) - visible_len("[ ]")
        header_label = _fit_header_label(header_label, max_label)
        if header_label:
            inner = "[ " + header_label + " ]"
        else:
            inner = "[ ]"
        inner_len = visible_len(inner)
        fill_len = outer_width - visible_len(prefix) - visible_len(end) - inner_len
        if fill_len < 0:
            fill_len = 0
    return prefix + inner + _repeat_char(cs["top_fill"], fill_len) + end


def _body_line(line, inner_width, cs):
    return cs["body_left"] + _pad_line(line, inner_width) + cs["body_right"]


def _bottom_border(outer_width, cs):
    mid = outer_width - visible_len(cs["bottom_left"]) - visible_len(cs["bottom_right"])
    if mid < 0:
        mid = 0
    return cs["bottom_left"] + _repeat_char(cs["bottom_fill"], mid) + cs["bottom_right"]


def _render_plain(lines):
    for line in lines:
        print(line)


def _render_plain_npc(display, lines):
    prefix = display + ": "
    indent = " " * visible_len(prefix)
    for i, line in enumerate(lines):
        if i == 0:
            print(prefix + line)
        else:
            print(indent + line)


def _render_plain_notify(header, lines):
    prefix = ("[" + header + "] ") if header else ""
    indent = " " * visible_len(prefix)
    for i, line in enumerate(lines):
        if i == 0:
            print(prefix + line)
        else:
            print(indent + line)


def render_box_lines(header_display, lines, style, with_person=False, for_pager=False):
    detected = terminal_cols()
    if detected < _MIN_DETECTED:
        if style == "npc":
            out = [header_display + ":"]
            out.extend(lines)
            return out
        prefix = ("[" + header_display + "] ") if header_display else ""
        out = []
        for i, line in enumerate(lines):
            if i == 0:
                out.append(prefix + line)
            else:
                out.append((" " * visible_len(prefix)) + line)
        return out

    outer_width = _outer_width_for_box(header_display, for_pager=for_pager)
    cs = _charset(style, for_pager=for_pager)
    body_pad = visible_len(cs["body_left"]) + visible_len(cs["body_right"])
    inner_width = outer_width - body_pad
    if inner_width < 8:
        return list(lines)

    body = _wrap_body_lines(lines, inner_width)
    if style == "npc":
        top = _top_border_labeled(
            header_display, outer_width, cs, with_person=with_person, for_pager=for_pager
        )
    else:
        top = _top_border_notify(header_display, outer_width, cs)
    bottom = _bottom_border(outer_width, cs)

    out = [top]
    for line in body:
        out.append(_body_line(line, inner_width, cs))
    out.append(bottom)
    return out


def render_box(header_display, header_ansi, lines, style, with_person=False):
    detected = terminal_cols()
    if detected < _MIN_DETECTED:
        if style == "npc":
            _render_plain_npc(header_display, lines)
        else:
            _render_plain_notify(header_display, lines)
        return

    outer_width = _outer_width_for_box(header_display)
    cs = _charset(style)
    body_pad = visible_len(cs["body_left"]) + visible_len(cs["body_right"])
    inner_width = outer_width - body_pad
    if inner_width < 8:
        _render_plain(lines)
        return

    box_lines = render_box_lines(header_display, lines, style, with_person=with_person)
    print("\n".join(box_lines))


def _player_status_blocks(sections, for_pager=False):
    blocks = []
    first = True
    for section in sections:
        kind = section[0]
        title = section[1]
        lines = list(section[2])
        if for_pager:
            lines = [_strip_ui_symbols(str(line)) for line in lines]
        if kind == "main":
            header = _player_main_header(for_pager)
            style = "notify"
        else:
            header = _player_section_header(kind, title, for_pager)
            style = "npc"
        if not first:
            blocks.append("")
        first = False
        blocks.extend(render_box_lines(header, lines, style, for_pager=for_pager))
    return blocks


def show_player_status(sections):
    ascii_pager = _pager_use_ascii()
    blocks = _player_status_blocks(sections, for_pager=ascii_pager)
    text = "\n".join(blocks)
    pager_show(text, ascii_pager=ascii_pager)


def say_npc(speaker, text):
    if text is None:
        text = ""
    text = str(text)
    if not text.strip():
        return
    display = _display_name(speaker)
    detected = terminal_cols()
    if detected < _MIN_DETECTED:
        width = max(10, detected - visible_len(display) - 2)
        lines = wrap_text(text, width)
        _render_plain_npc(display, lines)
        return
    cs = _charset("npc")
    body_pad = visible_len(cs["body_left"]) + visible_len(cs["body_right"])
    inner_width = _box_width() - body_pad
    if inner_width < 8:
        lines = wrap_text(text, max(10, detected - visible_len(display) - 2))
        _render_plain_npc(display, lines)
        return
    lines = wrap_text(text, inner_width)
    render_box(display, bold(display), lines, "npc", with_person=True)


def notify(kind, text):
    if text is None:
        text = ""
    text = str(text)
    if not text.strip():
        return
    base_header = _NOTIFY_HEADERS.get(kind, "")
    header = _notify_header_text(kind, base_header)
    detected = terminal_cols()
    if detected < _MIN_DETECTED:
        prefix_len = visible_len(header) + 3 if header else 0
        width = max(10, detected - prefix_len)
        lines = wrap_text(text, width)
        _render_plain_notify(header, lines)
        return
    cs = _charset("notify")
    body_pad = visible_len(cs["body_left"]) + visible_len(cs["body_right"])
    inner_width = _box_width() - body_pad
    if inner_width < 8:
        prefix_len = visible_len(header) + 3 if header else 0
        lines = wrap_text(text, max(10, detected - prefix_len))
        _render_plain_notify(header, lines)
        return
    lines = wrap_text(text, inner_width)
    render_box(header, header, lines, "notify")
