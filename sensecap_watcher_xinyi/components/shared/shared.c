/**
 * @file shared.c
 * @brief Minimal source file so shared component can be built.
 */

#include "esp_log.h"

static const char *TAG = "SHARED";

void shared_component_dummy(void)
{
    ESP_LOGD(TAG, "Shared component active");
}
