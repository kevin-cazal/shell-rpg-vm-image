/*
 * (Re)mount virtio-9p host9p at /mnt/host. Installed setuid root for user42.
 * Shell scripts cannot use setuid on Linux; this must be a real binary.
 */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define MOUNT_POINT "/mnt/host"
#define MOUNT_SRC "host9p"
#define MOUNT_FSTYPE "9p"
#define MOUNT_OPTS "trans=virtio,version=9p2000.L"

static void run_modprobe(const char *mod)
{
	pid_t pid = fork();

	if (pid < 0)
		return;
	if (pid == 0) {
		execl("/sbin/modprobe", "modprobe", mod, (char *)NULL);
		execl("/bin/modprobe", "modprobe", mod, (char *)NULL);
		_exit(127);
	}
	waitpid(pid, NULL, 0);
}

int main(void)
{
	umount2(MOUNT_POINT, MNT_DETACH);

	run_modprobe("9pnet_virtio");
	run_modprobe("9p");

	if (mount(MOUNT_SRC, MOUNT_POINT, MOUNT_FSTYPE, 0, MOUNT_OPTS) != 0) {
		fprintf(stderr, "mount-host-share: mount %s: %s\n", MOUNT_POINT,
			strerror(errno));
		return 1;
	}
	return 0;
}
