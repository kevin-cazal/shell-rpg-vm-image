/*
 * Read host→guest bytes from /dev/hvc1, emit complete lines on stdout (UTF-8).
 * For use with a shell handler: vm-bridge-listen | while read -r line; do …; done
 *
 * Reopens /dev/hvc1 after EOF so a short disconnect does not end the daemon.
 */
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "vm-bridge-debug.h"

#define HVC_PATH "/dev/hvc1"
#define BUF_SIZE 4096
#define LINE_CAP (256 * 1024)

static uint8_t *line_buf;
static size_t line_len;

static int flush_line(void)
{
	size_t start = 0;
	while (start < line_len) {
		size_t end = start;
		while (end < line_len && line_buf[end] != '\n')
			end++;
		if (end >= line_len)
			break;
		{
			size_t out_len = end - start;
			if (out_len > 0 && line_buf[end - 1] == '\r')
				out_len--;
			if (out_len > 0 &&
			    fwrite(line_buf + start, 1, out_len, stdout) != out_len)
				return -1;
			vmb_debugf("vm-bridge-listen", "emit line len=%zu preview=%.64s%s\n",
			    out_len, (const char *)(line_buf + start),
			    out_len > 64 ? "…" : "");
			if (fputc('\n', stdout) == EOF)
				return -1;
		}
		start = end + 1;
	}
	if (start > 0) {
		memmove(line_buf, line_buf + start, line_len - start);
		line_len -= start;
	}
	return 0;
}

static int append_bytes(const uint8_t *data, size_t n)
{
	if (line_len + n > LINE_CAP)
		return -1;
	memcpy(line_buf + line_len, data, n);
	line_len += n;
	return flush_line();
}

static int listen_once(void)
{
	uint8_t chunk[BUF_SIZE];
	ssize_t n;
	int hvc_fd;

	hvc_fd = open(HVC_PATH, O_RDONLY);
	if (hvc_fd < 0) {
		perror(HVC_PATH);
		return -1;
	}

	while ((n = read(hvc_fd, chunk, sizeof(chunk))) > 0) {
		if (append_bytes(chunk, (size_t)n) != 0) {
			close(hvc_fd);
			return -1;
		}
	}

	close(hvc_fd);
	return (n < 0) ? -1 : 0;
}

int main(void)
{
	line_buf = malloc(LINE_CAP);
	if (!line_buf)
		return 1;
	line_len = 0;

	for (;;) {
		if (listen_once() != 0)
			return 1;
		line_len = 0;
	}
}
