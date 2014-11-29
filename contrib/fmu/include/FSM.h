#ifndef __FSM_H__
#define __FSM_H__

#include <stdlib.h>
#include "mealydata.h"

typedef struct FSM {
	int currentState;
} FSM;

FSM* init_fsm();

int fsm_transition(FSM* fsm, int input[]);

void free_fsm(FSM* fsm);
#endif
