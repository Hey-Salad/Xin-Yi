/**
 * @file xinyi_client_stub.c
 * @brief Xin-Yi backend client helpers (stub implementation).
 */

#include "xinyi_client.h"
#include "esp_log.h"

static const char *TAG = "XINYI_CLIENT";

void xinyi_client_init(app_state_t *state)
{
    ESP_LOGI(TAG, "Backend client ready, target=%s", state->backend_url);
    state->backend_connected = true;
}
