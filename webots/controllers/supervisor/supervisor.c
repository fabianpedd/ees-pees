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

	// establish coms to backend
	







	const int seed = time(NULL);
	srand(seed);

	WbNodeRef objects_group_node = wb_supervisor_node_get_from_def("Objects");
	WbFieldRef group_children_field = wb_supervisor_node_get_field(objects_group_node, "children");

	rand_place_obstacles(19, group_children_field);

	int c = 0;

	if (timestep == 0)
	timestep = 1;
	while (wb_robot_step(timestep) != -1) {
		//const double current_time = wb_robot_get_time();
		// Generate a world every 60 timesteps for testing purposes
		if(c >= 60) {
			c = 0;
			wb_supervisor_simulation_reset();
		} else if (c == 0) {
			rand_place_obstacles(19, group_children_field);
			c++;
		} else {
			c++;
		}
	};

	wb_robot_cleanup();

	return EXIT_SUCCESS;
}
