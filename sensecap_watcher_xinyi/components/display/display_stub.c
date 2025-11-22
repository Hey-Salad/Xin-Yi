/**
 * @file display_stub.c
 * @brief Minimal display helpers simulated for development.
 */

#include "display.h"
#include "esp_log.h"

static const char *TAG = "DISPLAY";

void display_init(app_state_t *state)
{
    ESP_LOGI(TAG, "Display module ready (simulated)");
    state->display_ready = true;
}

void display_draw_status(app_state_t *state)
{
    if (!state->display_ready) {
        return;
    }
    ESP_LOGI(TAG, "Display update | WiFi=%d Backend=%d Role=%d Uptime=%lus",
             state->wifi_connected,
             state->backend_connected,
             state->role,
             state->uptime_seconds);
}
