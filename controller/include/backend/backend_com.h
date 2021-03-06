#ifndef COM_H
#define COM_H

#define DIST_VECS    360

enum response_request {
	UNDEF = 0,                  // Invalid Packet
	COMMAND_ONLY = 1,           // Only new instructions for Robot, dont send next packet
	REQUEST_ONLY = 2,           // Only request for new packet
	COMMAND_REQUEST = 3,        // New instructions for robot AND request for new packet
	GRID_MOVE = 4               // Send new packet once discrete action is done
};
extern const char* response_request_str[];

enum discrete_move {
	NONE = 0,                   // Dont do a discrete move at all, do continous
	UP = 1,                     // Move Up
	LEFT = 2,                   // Move Left
	DOWN = 3,                   // Move Down
	RIGHT = 4                   // Move Right
};
extern const char* discrete_move_str[];

enum direction_type {
	STEERING = 0,               // The backend commands the steering of the robot
	HEADING = 1,                // The backend commands the heading the robot should drive in
};
extern const char* direction_type_str[];


// DATA TO BACKEND
// Packet that contains data that is send to the backend
typedef struct {
	unsigned long long msg_cnt;    // total number of messages (internal)
	double time_stmp;              // time the message got send (internal)
	float sim_time;                // actual simulation time in webots in seconds
	float speed;                   // current speed of robot in webots [-1, 1]
	float actual_gps[2];           // coordinates where the robot is
	float heading;                 // direction the front of the robot points in [-1, 1]
	float steer_angle;             // current angle of the steering apparatus [-1, 1]
	unsigned int touching;         // is the robot touching something or tipped over
	unsigned int action_denied;    // did we have to take over control for saftey reasons
	unsigned int discr_act_done;   // did the robot complete its discrete action
	float distance[DIST_VECS];     // distance to the next object from robot prespective
} __attribute__((packed)) data_to_bcknd_msg_t;


// COMMAND FROM BACKEND
// Packet that contains command and command type from backend
typedef struct {
	unsigned long long msg_cnt;    // total number of messages (internal)
	double time_stmp;              // time the message got send (internal)
	int every_x;                   // number of timesteps before new data is send
	int disable_safety;            // do not use safety in the external controller
	enum response_request request; // type of response the backend awaits to the packet
	enum discrete_move move;       // ignore command parameters and do a discrete_action
	enum direction_type dir_type;  // heading or steering command from backend
	float heading;                 // the direction the robot should move in next [-1, 1]
	float speed;                   // the speed the robot should drive at [-1, 1]
} __attribute__((packed)) cmd_from_bcknd_msg_t;


int com_init();

int com_deinit();

float link_quality(float amt);

int com_send(data_to_bcknd_msg_t data);

int com_recv(cmd_from_bcknd_msg_t *data);

#endif // COM_H
