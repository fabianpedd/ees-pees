#ifndef UTIL_H
#define UTIL_H

#include "internal_com.h"

#define min(X, Y) (((X) < (Y)) ? (X) : (Y))
#define max(X, Y) (((X) > (Y)) ? (X) : (Y))

int time_diff_start(double *time);

int time_diff_stop(double *time);

int delay(double s);

double get_time();

void print_wb_to_ext(wb_to_ext_msg_t wb_to_ext);

void error(char* reason);

#endif // UTIL_H