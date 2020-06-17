#ifndef NAVI_H
#define NAVI_H

#include "webots/wb_com.h"
#include "backend/backend_com.h"

int navi_init();

int navigate(ext_to_wb_msg_t *ext_to_wb, ext_to_bcknd_msg_t ext_to_bcknd,
             init_to_ext_msg_t init_data, float dest[]);

int navi_check_back(float start_heading, float dest_heading);

float navi_get_heading(float start[], float dest[]);

float navi_get_distance(float start[], float dest[]);

float navi_inv_heading(float heading);

#endif // NAVI_H
