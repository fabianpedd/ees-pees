#include "../include/sv_com.h"

#include <stdio.h>
#include <string.h>

#include "../include/tcp.h"
#include "../include/util.h"


int sv_connect(){

	int ret_connect = tcp_connect();
	return ret_connect;
}

int sv_send(sv_to_bcknd_msg_t data) {

	int len = tcp_send((char *) &data, sizeof(sv_to_bcknd_msg_t));
	if (len < (int) sizeof(sv_to_bcknd_msg_t)) {
		fprintf(stderr, "ERROR(supervisor_com): Did not send complete data. Bytes send: %d'\n", len);
		return -1;
	}

	return 0;
}

int sv_recv(bcknd_to_sv_msg_t *data) {

	memset(data, 0, sizeof(bcknd_to_sv_msg_t));

	int len = tcp_recv((char *)data, sizeof(bcknd_to_sv_msg_t));
	if (len < (int) sizeof(bcknd_to_sv_msg_t)) {
		fprintf(stderr, "ERROR(supervisor_com): Did not receive complete data. Bytes received: %d'\n", len);
		return -1;
	}

	return 0;
}

int sv_close() {

	return tcp_close();
}
