/*
* Copyright 1996-2020 Cyberbotics Ltd.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

#include <webots/robot.h>
#include <webots/supervisor.h>

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "sv_com.h"
#include "sv_functions.h"


/*** ----------------------------- ***

TODOs -block constraints:  not where robot/goal is
not 2 at a same point
such that goal is reachable

-place robot and goal randomly and save goal coords for internal controller

-stop and restart internal controller for each run is slow
so just move their positions instead

INFO: block-coords_ a[-10 to 9], b[-10 to 9]

*** ----------------------------- ***/





int main() {

	wb_robot_init();
	int timestep = wb_robot_get_basic_time_step();

	/**************** COMMUNICATION***************************/
	/*********** comment out if testing without backend*******/

	// establish coms to backend
	int ret_connect = sv_connect();
	if(ret_connect) {
		fprintf(stderr, "SUPERVISOR: Can't connect to backend\n");
	}

	// recv test message
	bcknd_to_sv_msg_t test_buf;
	sv_recv(&test_buf);

	printf("=========== Received Test msg ===========\n");
	printf("function_code: %d\n", test_buf.function_code);
	printf("seed: %d\n", test_buf.seed);
	printf("fast_simulation: %d\n", test_buf.fast_simulation);
	printf("num_obstacles: %d\n", test_buf.num_obstacles);
	printf("world_size: %d\n", test_buf.world_size);
	printf("target_x: %f\n", test_buf.target_x);
	printf("target_y: %f\n", test_buf.target_y);
	printf("=========================================\n");

	// send test message
	sv_to_bcknd_msg_t test_msg;
	test_msg.return_code = 1;
	test_msg.lidar_min_range = 0.04;
	test_msg.lidar_max_range = 3.4;
	test_msg.sim_time_step = timestep;

	sv_send(test_msg);
	printf("=========== Sending Test msg  successful ===========\n");


	/**************** COMMUNICATION END **********************/

	//---TODO AREA -- reset performed in here if necessary and keep in mind, that reset needs a time step


	if (timestep == 0)
	timestep = 1;
	while (wb_robot_step(timestep) != -1) {
		//const double current_time = wb_robot_get_time();
	};
	//wb_supervisor_simulation_quit(EXIT_SUCCESS); //terminates the program/leave while loop
	
	//----TODO AREA END
	// Termination routine should only be down here
	
	//sv_simulation_cleanup();
	wb_robot_cleanup();

	return EXIT_SUCCESS;
}
