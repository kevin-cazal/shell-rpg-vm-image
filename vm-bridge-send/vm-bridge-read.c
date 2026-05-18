/*
 * Copy host→guest bytes from /dev/hvc1 to stdout or a file (raw, no framing).
 *
 * Usage: vm-bridge-read -              # stdout until EOF on hvc1
 *        vm-bridge-read <file>         # write to file
 */
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

#define HVC_PATH "/dev/hvc1"
#define BUF_SIZE 4096

int main(int argc, char **argv)
{
	int out_fd = STDOUT_FILENO;
	int hvc_fd;
	char buf[BUF_SIZE];
	ssize_t n;

	if (argc >= 2 && argv[1][0] == '-' && argv[1][1] == '\0') {
		/* stdout */
	} else if (argc >= 2) {
		out_fd = open(argv[1], O_WRONLY | O_CREAT | O_TRUNC, 0666);
		if (out_fd < 0) {
			perror(argv[1]);
			return 1;
		}
	} else {
		return 0;
	}

	hvc_fd = open(HVC_PATH, O_RDONLY);
	if (hvc_fd < 0) {
		perror(HVC_PATH);
		if (out_fd != STDOUT_FILENO)
			close(out_fd);
		return 1;
	}

	while ((n = read(hvc_fd, buf, sizeof(buf))) > 0) {
		ssize_t off = 0;
		while (off < n) {
			ssize_t w = write(out_fd, buf + off, (size_t)(n - off));
			if (w < 0) {
				close(hvc_fd);
				if (out_fd != STDOUT_FILENO)
					close(out_fd);
				return 1;
			}
			off += w;
		}
	}

	close(hvc_fd);
	if (out_fd != STDOUT_FILENO)
		close(out_fd);
	return (n < 0) ? 1 : 0;
}
