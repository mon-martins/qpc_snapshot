/************************************************************/
// Automatically generated C source file
// Date created: 2025-10-04
/************************************************************/

#include "qp_snapshot.h"


// ================================================================================
// State machine from file "blinky.h"
// ================================================================================

uint64_t blinky_get_current_state(QAsm const * const state_machine) {
    uint64_t current_state = 0;
    current_state |= ((uint64_t) QASM_IS_IN(state_machine, blinky_off) << BLINKY_OFF);
    current_state |= ((uint64_t) QASM_IS_IN(state_machine, blinky_on) << BLINKY_ON);
    return current_state;
}
