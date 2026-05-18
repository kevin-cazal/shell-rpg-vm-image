import os
import sys

try:
    import hashlib
except ImportError:
    hashlib = None

try:
    import ubinascii
except ImportError:
    ubinascii = None

try:
    import base64 as _base64
except ImportError:
    _base64 = None

if _base64 is None and ubinascii is not None:

    class _Base64:
        @staticmethod
        def b64decode(data):
            return ubinascii.a2b_base64(data)

    base64 = _Base64()
else:
    base64 = _base64

_S_IFMT = 0o170000
_S_IFDIR = 0o040000
_S_IFREG = 0o100000
_S_IFLNK = 0o120000


def _stat_mode(path):
    return os.stat(path)[0]


def _exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


class _OsPath:
    sep = "/"

    def join(self, *parts):
        out = ""
        for part in parts:
            if not part:
                continue
            if not out:
                out = part
            else:
                if not out.endswith("/"):
                    out += "/"
                if part.startswith("/"):
                    part = part[1:]
                out += part
        return out

    def normpath(self, path):
        parts = []
        for part in path.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return "/" + "/".join(parts) if path.startswith("/") else "/".join(parts)

    def dirname(self, path):
        if "/" not in path:
            return ""
        return path.rsplit("/", 1)[0]

    def basename(self, path):
        return path.rsplit("/", 1)[-1]

    exists = staticmethod(_exists)

    def isdir(self, path):
        try:
            return (_stat_mode(path) & _S_IFMT) == _S_IFDIR
        except OSError:
            return False

    def isfile(self, path):
        try:
            return (_stat_mode(path) & _S_IFMT) == _S_IFREG
        except OSError:
            return False

    def islink(self, path):
        try:
            return (_stat_mode(path) & _S_IFMT) == _S_IFLNK
        except OSError:
            return False

    def readlink(self, path):
        tmp = "/tmp/.mpy_readlink"
        os.system("readlink -n " + path + " > " + tmp + " 2>/dev/null")
        try:
            with open(tmp, "r") as f:
                return f.read().strip()
        except OSError:
            return ""

    def samefile(self, a, b):
        try:
            sa = os.stat(a)
            sb = os.stat(b)
            return sa[1] == sb[1] and sa[2] == sb[2]
        except OSError:
            return False


def _walk(top):
    stack = [top]
    while stack:
        root = stack.pop()
        try:
            names = os.listdir(root)
        except OSError:
            continue
        dirs = []
        files = []
        for name in names:
            if root == "/":
                path = "/" + name
            elif root.endswith("/"):
                path = root + name
            else:
                path = root + "/" + name
            try:
                mode = _stat_mode(path)
            except OSError:
                files.append(name)
                continue
            if (mode & _S_IFMT) == _S_IFDIR:
                dirs.append(name)
                stack.append(path)
            else:
                files.append(name)
        yield root, dirs, files


def _makedirs(path, exist_ok=False):
    if exist_ok and _exists(path):
        return
    os.system("mkdir -p " + path)


def _chmod(path, mode):
    os.system("chmod %o %s 2>/dev/null" % (mode, path))


def _symlink(target, link):
    os.system("ln -sf " + target + " " + link)


def _sha256_hex(data):
    if hashlib is None:
        raise ImportError("hashlib required")
    digest = hashlib.sha256(data)
    if hasattr(digest, "hexdigest"):
        return digest.hexdigest()
    return ubinascii.hexlify(digest.digest()).decode()


class _OsWrapper:
    def __init__(self, real_os):
        self._real = real_os
        self.path = _OsPath()

    def __getattr__(self, name):
        return getattr(self._real, name)


def patch_runtime():
    global os
    try:
        has_join = hasattr(os.path, "join")
    except AttributeError:
        has_join = False
    if not has_join:
        wrapped = _OsWrapper(os)
        for name, func in (
            ("exists", _exists),
            ("walk", _walk),
            ("makedirs", _makedirs),
            ("chmod", _chmod),
            ("symlink", _symlink),
        ):
            setattr(wrapped, name, func)
        sys.modules["os"] = wrapped
        os = wrapped
        return
    for name, func in (
        ("exists", _exists),
        ("walk", _walk),
        ("makedirs", _makedirs),
        ("chmod", _chmod),
        ("symlink", _symlink),
    ):
        if not hasattr(os, name):
            setattr(os, name, func)
    if hashlib is not None and ubinascii is not None:
        try:
            hashlib.sha256(b"x").hexdigest()
        except AttributeError:
            _orig = hashlib.sha256

            def sha256(data):
                digest = _orig(data)
                if not hasattr(digest, "hexdigest"):
                    digest.hexdigest = lambda: ubinascii.hexlify(digest.digest()).decode()
                return digest

            hashlib.sha256 = sha256


patch_runtime()


def copyfile(src, dst):
    with open(src, "rb") as fsrc:
        data = fsrc.read()
    with open(dst, "wb") as fdst:
        fdst.write(data)


def get_username():
    return os.getenv("USER") or "user42"


def capitalize(s):
    s = s.lower()
    return s[0].upper() + s[1:] if s else s
