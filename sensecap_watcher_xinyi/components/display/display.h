/**
 * @file display.h
 * @brief Display helpers for the 412x412 screen.
 */

#ifndef DISPLAY_H
#define DISPLAY_H

#include "app_state.h"

#ifdef __cplusplus
extern "C" {
#endif

void display_init(app_state_t *state);
void display_draw_status(app_state_t *state);

#ifdef __cplusplus
}
#endif

#endif // DISPLAY_H
