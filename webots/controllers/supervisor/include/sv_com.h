#ifndef SV_COM_H
#define SV_COM_H

#include "../include/sv_functions.h"

enum function_code {
	FUNC_UNDEF = -1,
	NO_FUNCTION = 0,
	START = 1,
	RESET = 2,
	CLOSE = 3
};

enum return_code {
	RET_UNDEF = -1,
	SUCCESS = 0,
	ERROR = 1
};

// supervisor --> backend
typedef struct {
	enum return_code return_code;     // return_code [enum return_code]
	int sim_time_step;                // simulation time_step in ms [int]
	float target[2];                  // target position [float[2]]
} __attribute__((packed)) sv_to_bcknd_msg_t;

// supervisor <-- backend
typedef struct {
	enum function_code function_code; // function code [enum function_code]
	int seed;                         // seed [int]
	enum sv_sim_mode mode;            // fast_simulation [enum sv_sim_mode]
	int num_obstacles;                // num_obstacles [int]
	int world_size;                   // world_size in blocks [int]
	float scale;                      // scale of the world, actual_size = world_size*scale [float]
} __attribute__((packed)) bcknd_to_sv_msg_t;


int sv_connect();

int sv_send(sv_to_bcknd_msg_t data);

int sv_recv(bcknd_to_sv_msg_t *data);

int sv_close();


#endif //SV_COM_H
