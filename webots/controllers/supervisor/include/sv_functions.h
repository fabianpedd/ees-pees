#ifndef SV_FUNCTIONS_H
#define SV_FUNCTIONS_H


#include <webots/robot.h>
#include <webots/supervisor.h>

enum sv_sim_mode {
	NORMAL = 0,
	RUN    = 1,
	FAST   = 2
};

typedef struct {
	int num_obstacles;                    // number of obstacles
	int size;                             // size in blocks
	double scale;                         // size of each block in webots coordinates
	double start[2];                      // starting coordinates
	double target[2];                     // target coordinates
	enum sv_sim_mode mode;                // simulation speed
	WbNodeRef robot_node;                 // reference to robot node
	WbFieldRef target_translation_field;  // reference to modify target position
	WbFieldRef children_field;            // reference to the obstacles group children
	int timestep;                         // length of a timestep in ms
} sv_world_def;


double sv_to_coord(sv_world_def *world, int xy);

int sv_from_coord(sv_world_def *world, double xy);

void sv_obstacle_spawn(sv_world_def *world);

void sv_obstacle_put(sv_world_def *world, int x, int y, int id);

void sv_obstacle_put_all(sv_world_def *world);

void sv_world_init(sv_world_def *world, int world_size, double scale, int num_obstacles, enum sv_sim_mode mode);

void sv_world_generate(sv_world_def *world, int seed);

void sv_world_clear(sv_world_def *world);

sv_world_def *sv_simulation_init();

void sv_simulation_start(sv_world_def *world);

void sv_simulation_stop();

void sv_simulation_update(sv_world_def *world);

void sv_simulation_cleanup(sv_world_def *world);


#endif //SV_FUNCTIONS_H
