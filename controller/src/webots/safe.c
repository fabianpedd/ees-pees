#include "webots/safe.h"

#include <math.h>

#include "backend/backend_com.h"
#include "silhouette.h"

int safety_check(init_to_ext_msg_t init_data, data_to_bcknd_msg_t data_to_bcknd,
	             cmd_to_ext_msg_t* cmd_to_ext) {

	(void) init_data;
	(void) data_to_bcknd;
	(void) cmd_to_ext;

	// TODO: here we need to check if we are hitting smth and if
	// so we need to set the speed (and maybe heading) to 0  or smth similar

	// maybe: if hitting then
	// cmd_to_ext->speed = 0;
	// cmd_to_ext->heading = 0;

	// return 0 if action was okay
	// return 1 if we had to take over control for safety reasons
	return 0;
}

int touching(float dist[]) {

	int touching = 0;
	int currently_touching = 0;
	for (int i=0; i<DIST_VECS; i++) {
		if (dist[i] < silhouette[i] && currently_touching == 0) {
			currently_touching = 1;
		} else if (!(dist[i] < silhouette[i]) && currently_touching == 1) {
			currently_touching = 0;
			touching ++;
		}
	}

	return touching;
}


int check_for_tipover(data_to_ext_msg_t data_to_ext) {

	if (fabs(data_to_ext.actual_gps[1] - 0.026) > 0.02) {
		return -1;
	} else {
		return 0;
	}
}
