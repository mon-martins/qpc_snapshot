/************************************************************/
// Automatically generated C header file
// Date created: 2025-10-04
/************************************************************/

#include "qpc.h"


// ================================================================================
// State machine from file "blinky.h"
// ================================================================================

typedef enum snapshot_blinky {
    BLINKY_OFF = 0,
    BLINKY_ON = 1,
    SNAPSHOT_BLINKY_NUMBER_OF_VALUES
} snapshot_blinky_t;

uint64_t blinky_get_current_state(QAsm const * const state_machine);

