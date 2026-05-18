/*
 * Guest vm-bridge tools: stderr logging when VM_BRIDGE_DEBUG is set (non-empty, not "0").
 */
#ifndef VM_BRIDGE_DEBUG_H
#define VM_BRIDGE_DEBUG_H

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>

static inline int vmb_debug_enabled(void)
{
	const char *e = getenv("VM_BRIDGE_DEBUG");

	return e && e[0] && e[0] != '0';
}

static inline void vmb_debugf(const char *tag, const char *fmt, ...)
{
	va_list ap;

	if (!vmb_debug_enabled())
		return;
	fprintf(stderr, "[%s] ", tag);
	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);
}

#endif
