/**
 * @file app_state.h
 * @brief Application-wide state shared between modules.
 */

#ifndef APP_STATE_H
#define APP_STATE_H

#include <stdint.h>
#include <stdbool.h>

#include "config.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    bool wifi_connected;
    bool backend_connected;
    bool camera_ready;
    bool display_ready;
    bool streaming_enabled;
    uint32_t uptime_seconds;
    uint32_t frames_sent;
    float battery_voltage;
    char device_id[37];
    char wifi_ssid[32];
    char wifi_password[64];
    char backend_url[128];
    device_role_t role;
} app_state_t;

extern app_state_t g_app_state;

#ifdef __cplusplus
}
#endif

#endif // APP_STATE_H
