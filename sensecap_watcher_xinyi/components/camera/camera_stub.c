/**
 * @file camera_stub.c
 * @brief Camera helpers placeholder for the Himax processor.
 */

#include "camera.h"
#include "esp_log.h"

static const char *TAG = "CAMERA";

void camera_init(app_state_t *state)
{
    ESP_LOGI(TAG, "Camera module initialized (stub)");
    state->camera_ready = true;
}
