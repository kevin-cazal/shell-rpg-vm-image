/*
 * Write raw bytes to /dev/hvc1 (no newline). Setuid root for user42.
 *
 * Usage: vm-bridge-raw <file>
 *        vm-bridge-raw -          # stdin until EOF
 */
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/file.h>

#include "vm-bridge-debug.h"

#define LOCK_PATH "/tmp/.vm-bridge.lock"
#define HVC_PATH  "/dev/hvc1"
#define BUF_SIZE  4096

static int copy_stream(int in_fd)
{
	int lock_fd;
	int hvc_fd;
	char buf[BUF_SIZE];
	ssize_t n;
	size_t total_in = 0;
	size_t total_out = 0;
	size_t newline_count = 0;
	unsigned read_chunks = 0;
	unsigned write_ops = 0;

	lock_fd = open(LOCK_PATH, O_CREAT | O_RDWR, 0666);
	if (lock_fd < 0)
		return 1;
	if (flock(lock_fd, LOCK_EX) != 0) {
		close(lock_fd);
		return 1;
	}

	hvc_fd = open(HVC_PATH, O_WRONLY | O_APPEND);
	if (hvc_fd < 0) {
		vmb_debugf("vm-bridge-raw", "open %s failed\n", HVC_PATH);
		flock(lock_fd, LOCK_UN);
		close(lock_fd);
		return 1;
	}

	while ((n = read(in_fd, buf, sizeof(buf))) > 0) {
		read_chunks++;
		total_in += (size_t)n;
		for (ssize_t i = 0; i < n; i++) {
			if (buf[i] == '\n')
				newline_count++;
		}
		ssize_t off = 0;
		while (off < n) {
			ssize_t w = write(hvc_fd, buf + off, (size_t)(n - off));
			if (w < 0) {
				vmb_debugf("vm-bridge-raw", "write failed after in=%zu out=%zu\n",
				    total_in, total_out);
				close(hvc_fd);
				flock(lock_fd, LOCK_UN);
				close(lock_fd);
				return 1;
			}
			write_ops++;
			total_out += (size_t)w;
			off += w;
		}
	}

	vmb_debugf("vm-bridge-raw",
	    "done in=%zu out=%zu read_chunks=%u write_ops=%u lines≈%zu\n",
	    total_in, total_out, read_chunks, write_ops, newline_count);
	close(hvc_fd);
	flock(lock_fd, LOCK_UN);
	close(lock_fd);
	return 0;
}

int main(int argc, char **argv)
{
	if (argc >= 2 && argv[1][0] == '-' && argv[1][1] == '\0')
		return copy_stream(STDIN_FILENO);

	if (argc < 2)
		return 0;

	{
		int in_fd = open(argv[1], O_RDONLY);
		if (in_fd < 0) {
			perror(argv[1]);
			return 1;
		}
		if (copy_stream(in_fd) != 0) {
			close(in_fd);
			return 1;
		}
		close(in_fd);
	}
	return 0;
}
