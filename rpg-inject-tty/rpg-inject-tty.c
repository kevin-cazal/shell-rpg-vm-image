/*
 * Inject bytes into a terminal as if typed (Linux TIOCSTI).
 * Requires: dev.tty.legacy_tiocsti=1 (see configure.sh).
 *
 * Usage: rpg-inject-tty <tty-device>           # read command from stdin
 *        rpg-inject-tty <tty-device> <text>    # inject literal text
 */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#ifndef TIOCSTI
#define TIOCSTI 0x5412
#endif

static int inject_char(int fd, char c)
{
	if (ioctl(fd, TIOCSTI, &c) < 0)
		return -1;
	return 0;
}

static int inject_string(int fd, const char *s)
{
	for (; *s; s++) {
		if (inject_char(fd, *s) < 0)
			return -1;
	}
	return 0;
}

static int inject_stream(int fd, FILE *in)
{
	char buf[256];
	size_t n;

	while ((n = fread(buf, 1, sizeof(buf), in)) > 0) {
		for (size_t i = 0; i < n; i++) {
			if (inject_char(fd, buf[i]) < 0)
				return -1;
		}
	}
	return ferror(in) ? -1 : 0;
}

int main(int argc, char **argv)
{
	if (argc < 2) {
		fprintf(stderr, "usage: %s <tty> [text]\n", argv[0]);
		return 2;
	}

	int fd = open(argv[1], O_RDWR | O_NOCTTY);
	if (fd < 0) {
		perror(argv[1]);
		return 1;
	}

	int rc;
	if (argc >= 3)
		rc = inject_string(fd, argv[2]);
	else
		rc = inject_stream(fd, stdin);

	if (rc < 0) {
		perror("TIOCSTI");
		close(fd);
		return 1;
	}

	close(fd);
	return 0;
}
