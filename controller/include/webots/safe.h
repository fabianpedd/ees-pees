#ifndef SAFE_H
#define SAFE_H

// This will contain all code to check if the robot collides with some object.
// This will then also provide funtions that help to keep the robot safe.

#include "webots/wb_com.h"
#include "backend/backend_com.h"

int safety_check(bcknd_to_ext_msg_t *bcknd_to_ext);

int touching(float dist[]);

int check_for_tipover(wb_to_ext_msg_t wb_to_ext);

#endif // SAFE_H
