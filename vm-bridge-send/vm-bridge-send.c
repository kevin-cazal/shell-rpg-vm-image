/*
 * Send one line to /dev/hvc1 (virtio-console port 1 → host vm-bridge).
 * Installed setuid root so user42 can write when the device is root-only.
 *
 * Usage: vm-bridge-send <text...>
 *        echo "..." | vm-bridge-send -
 */
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/file.h>

#include "vm-bridge-debug.h"

#define LOCK_PATH "/tmp/.vm-bridge.lock"
#define HVC_PATH  "/dev/hvc1"
#define LINE_MAX  4096

static int build_line(int argc, char **argv, char *out, size_t outsz)
{
	size_t n = 0;

	out[0] = '\0';
	for (int i = 1; i < argc; i++) {
		size_t len = strlen(argv[i]);
		if (i > 1) {
			if (n + 1 >= outsz)
				return -1;
			out[n++] = ' ';
			out[n] = '\0';
		}
		if (n + len >= outsz)
			return -1;
		memcpy(out + n, argv[i], len);
		n += len;
		out[n] = '\0';
	}
	return (int)n;
}

static int read_stdin_line(char *out, size_t outsz)
{
	size_t n = 0;
	int c;

	while (n + 1 < outsz && (c = getchar()) != EOF) {
		if (c == '\n')
			break;
		out[n++] = (char)c;
	}
	out[n] = '\0';
	return (n > 0 || feof(stdin)) ? (int)n : -1;
}

static int write_line(const char *line)
{
	int lock_fd;
	int hvc_fd;
	ssize_t w;

	lock_fd = open(LOCK_PATH, O_CREAT | O_RDWR, 0666);
	if (lock_fd < 0)
		return 1;
	if (flock(lock_fd, LOCK_EX) != 0) {
		close(lock_fd);
		return 1;
	}

	hvc_fd = open(HVC_PATH, O_WRONLY | O_APPEND);
	if (hvc_fd < 0) {
		vmb_debugf("vm-bridge-send", "open %s failed\n", HVC_PATH);
		flock(lock_fd, LOCK_UN);
		close(lock_fd);
		return 1;
	}

	w = dprintf(hvc_fd, "%s\n", line);
	vmb_debugf("vm-bridge-send", "wrote line len=%zu bytes=%zd preview=%.72s%s\n",
	    strlen(line), w, line, strlen(line) > 72 ? "…" : "");
	close(hvc_fd);
	flock(lock_fd, LOCK_UN);
	close(lock_fd);

	if (w < 0)
		vmb_debugf("vm-bridge-send", "dprintf failed\n");
	return (w < 0) ? 1 : 0;
}

int main(int argc, char **argv)
{
	char line[LINE_MAX];

	if (argc >= 2 && strcmp(argv[1], "-") == 0) {
		if (read_stdin_line(line, sizeof(line)) < 0)
			return 1;
		return write_line(line);
	}

	if (argc < 2)
		return 0;

	if (build_line(argc, argv, line, sizeof(line)) < 0)
		return 1;

	return write_line(line);
}
