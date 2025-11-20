/**
 * @file main.c
 * @brief Main application for SenseCAP Watcher Xin-Yi Firmware
 *
 * Architecture inspired by heysalad_xiao_og but adapted for:
 * - ESP-IDF framework (instead of Arduino)
 * - SenseCAP Watcher hardware
 * - Xin-Yi logistics system integration
 *
 * Features:
 * - WiFi connectivity with AP fallback
 * - HTTP server with WebSocket support
 * - Camera streaming via Himax AI processor
 * - 412x412 touchscreen UI
 * - Integration with Xin-Yi Flask backend
 * - BLE for mobile app control
 * - SPIFFS for assets and configuration
 */

#include <stdio.h>
#include <string.h>
#include <sys/param.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

#include "esp_system.h"
#include "esp_mac.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_http_server.h"
#include "esp_spiffs.h"
#include "esp_timer.h"

#include "lwip/err.h"
#include "lwip/sys.h"

#include "include/config.h"

// =============================================================================
// LOGGING TAG
// =============================================================================
static const char *TAG = "XINYI_MAIN";

// =============================================================================
// GLOBAL STATE
// =============================================================================
typedef struct {
    bool wifi_connected;
    bool backend_connected;
    bool camera_ready;
    bool display_ready;
    bool streaming_enabled;
    uint32_t uptime_seconds;
    uint32_t frames_sent;
    float battery_voltage;
    char device_id[37];  // UUID
    char wifi_ssid[32];
    char wifi_password[64];
    char backend_url[128];
    device_role_t role;
} app_state_t;

static app_state_t g_app_state = {
    .wifi_connected = false,
    .backend_connected = false,
    .camera_ready = false,
    .display_ready = false,
    .streaming_enabled = true,
    .uptime_seconds = 0,
    .frames_sent = 0,
    .battery_voltage = 0.0f,
    .device_id = "",
    .wifi_ssid = WIFI_SSID_DEFAULT,
    .wifi_password = WIFI_PASSWORD_DEFAULT,
    .backend_url = XINYI_API_URL,
    .role = DEFAULT_DEVICE_ROLE
};

// =============================================================================
// FORWARD DECLARATIONS
// =============================================================================
static void init_nvs(void);
static void init_spiffs(void);
static void load_config_from_nvs(void);
static void save_config_to_nvs(void);
static void generate_device_id(void);
static void init_wifi(void);
static void init_display(void);
static void init_camera(void);
static void init_http_server(void);
static void init_bluetooth(void);
static void uptime_timer_callback(void *arg);
static void heartbeat_task(void *pvParameters);
static void display_status_screen(void);

// =============================================================================
// NVS INITIALIZATION
// =============================================================================
static void init_nvs(void)
{
    ESP_LOGI(TAG, "Initializing NVS...");
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "NVS partition was truncated, erasing...");
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    ESP_LOGI(TAG, "NVS initialized");
}

// =============================================================================
// SPIFFS INITIALIZATION
// =============================================================================
static void init_spiffs(void)
{
    ESP_LOGI(TAG, "Initializing SPIFFS...");

    esp_vfs_spiffs_conf_t conf = {
        .base_path = SPIFFS_BASE_PATH,
        .partition_label = NULL,
        .max_files = SPIFFS_MAX_FILES,
        .format_if_mount_failed = true
    };

    esp_err_t ret = esp_vfs_spiffs_register(&conf);

    if (ret != ESP_OK) {
        if (ret == ESP_FAIL) {
            ESP_LOGE(TAG, "Failed to mount or format filesystem");
        } else if (ret == ESP_ERR_NOT_FOUND) {
            ESP_LOGE(TAG, "Failed to find SPIFFS partition");
        } else {
            ESP_LOGE(TAG, "Failed to initialize SPIFFS (%s)", esp_err_to_name(ret));
        }
        return;
    }

    size_t total = 0, used = 0;
    ret = esp_spiffs_info(NULL, &total, &used);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to get SPIFFS partition information (%s)", esp_err_to_name(ret));
    } else {
        ESP_LOGI(TAG, "SPIFFS: Total: %d KB, Used: %d KB", total / 1024, used / 1024);
    }
}

// =============================================================================
// CONFIGURATION MANAGEMENT
// =============================================================================
static void load_config_from_nvs(void)
{
    ESP_LOGI(TAG, "Loading configuration from NVS...");
    nvs_handle_t nvs_handle;
    esp_err_t err;

    err = nvs_open("xinyi_config", NVS_READONLY, &nvs_handle);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "No saved configuration found, using defaults");
        return;
    }

    // Load WiFi credentials
    size_t ssid_len = sizeof(g_app_state.wifi_ssid);
    nvs_get_str(nvs_handle, "wifi_ssid", g_app_state.wifi_ssid, &ssid_len);

    size_t pass_len = sizeof(g_app_state.wifi_password);
    nvs_get_str(nvs_handle, "wifi_pass", g_app_state.wifi_password, &pass_len);

    // Load device ID
    size_t id_len = sizeof(g_app_state.device_id);
    err = nvs_get_str(nvs_handle, "device_id", g_app_state.device_id, &id_len);
    if (err != ESP_OK) {
        generate_device_id();
        save_config_to_nvs();  // Save generated ID
    }

    // Load backend URL
    size_t url_len = sizeof(g_app_state.backend_url);
    nvs_get_str(nvs_handle, "backend_url", g_app_state.backend_url, &url_len);

    // Load device role
    uint8_t role = DEFAULT_DEVICE_ROLE;
    nvs_get_u8(nvs_handle, "device_role", &role);
    g_app_state.role = (device_role_t)role;

    nvs_close(nvs_handle);
    ESP_LOGI(TAG, "Configuration loaded: Device ID = %s", g_app_state.device_id);
}

static void save_config_to_nvs(void)
{
    nvs_handle_t nvs_handle;
    esp_err_t err;

    err = nvs_open("xinyi_config", NVS_READWRITE, &nvs_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Failed to open NVS for writing: %s", esp_err_to_name(err));
        return;
    }

    nvs_set_str(nvs_handle, "wifi_ssid", g_app_state.wifi_ssid);
    nvs_set_str(nvs_handle, "wifi_pass", g_app_state.wifi_password);
    nvs_set_str(nvs_handle, "device_id", g_app_state.device_id);
    nvs_set_str(nvs_handle, "backend_url", g_app_state.backend_url);
    nvs_set_u8(nvs_handle, "device_role", (uint8_t)g_app_state.role);

    nvs_commit(nvs_handle);
    nvs_close(nvs_handle);

    ESP_LOGI(TAG, "Configuration saved to NVS");
}

static void generate_device_id(void)
{
    uint8_t mac[6];
    esp_efuse_mac_get_default(mac);

    snprintf(g_app_state.device_id, sizeof(g_app_state.device_id),
             "xinyi-watcher-%02x%02x%02x%02x%02x%02x",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    ESP_LOGI(TAG, "Generated device ID: %s", g_app_state.device_id);
}

// =============================================================================
// STUB FUNCTIONS (To be implemented in separate modules)
// =============================================================================

static void init_wifi(void)
{
    ESP_LOGI(TAG, "Initializing WiFi... (stub)");
    // TODO: Implement full WiFi manager in wifi_manager.c
    // Should handle:
    // - STA mode connection with retry
    // - AP mode fallback if no credentials
    // - mDNS service advertisement
    // - Network event handling
}

static void init_display(void)
{
    ESP_LOGI(TAG, "Initializing 412x412 display... (stub)");
    g_app_state.display_ready = false;
    // TODO: Implement in components/display/
    // Should handle:
    // - QSPI LCD initialization
    // - Touch screen calibration
    // - UI rendering framework
    // - Status display
}

static void init_camera(void)
{
    ESP_LOGI(TAG, "Initializing Himax camera... (stub)");
    g_app_state.camera_ready = false;
    // TODO: Implement in components/camera/
    // Should handle:
    // - Himax AI processor initialization
    // - Camera configuration
    // - Frame capture
    // - JPEG encoding
}

static void init_http_server(void)
{
    ESP_LOGI(TAG, "Starting HTTP server... (stub)");
    // TODO: Implement in http_server.c
    // Should provide:
    // - GET / - Web dashboard
    // - GET /api/status - Device status JSON
    // - POST /api/settings - Update configuration
    // - WS /ws - WebSocket for camera streaming
    // - POST /api/photo - Capture photo
}

static void init_bluetooth(void)
{
    ESP_LOGI(TAG, "Initializing Bluetooth... (stub)");
    // TODO: Implement BLE UART service
    // Compatible with heysalad_xiao_og BLE protocol
}

static void display_status_screen(void)
{
    // TODO: Render status on 412x412 display
    // Show:
    // - XinYi logo
    // - WiFi status
    // - Backend connection status
    // - Device role
    // - IP address
    // - Battery level
}

// =============================================================================
// PERIODIC TASKS
// =============================================================================

static void uptime_timer_callback(void *arg)
{
    g_app_state.uptime_seconds++;
}

static void heartbeat_task(void *pvParameters)
{
    ESP_LOGI(TAG, "Heartbeat task started");

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(BACKEND_HEARTBEAT_INTERVAL_MS));

        if (g_app_state.wifi_connected) {
            // TODO: Send heartbeat to Xin-Yi backend
            // POST to /api/devices/{device_id}/status
            ESP_LOGI(TAG, "Sending heartbeat to backend... (stub)");
        }

        // Update display
        if (g_app_state.display_ready) {
            display_status_screen();
        }
    }
}

// =============================================================================
// MAIN APPLICATION ENTRY POINT
// =============================================================================

void app_main(void)
{
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "  XinYi SenseCAP Watcher Firmware");
    ESP_LOGI(TAG, "  Version: %s", FIRMWARE_VERSION);
    ESP_LOGI(TAG, "  Device: %s", DEVICE_TYPE);
    ESP_LOGI(TAG, "========================================");

    // Initialize core systems
    init_nvs();
    init_spiffs();
    load_config_from_nvs();

    // Initialize hardware
    ESP_LOGI(TAG, "Initializing hardware...");
    init_display();
    init_camera();

    // Initialize networking
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    init_wifi();

    // Initialize services
    init_http_server();

    if (BLE_ENABLED) {
        init_bluetooth();
    }

    // Create uptime timer
    const esp_timer_create_args_t uptime_timer_args = {
        .callback = &uptime_timer_callback,
        .name = "uptime"
    };
    esp_timer_handle_t uptime_timer;
    ESP_ERROR_CHECK(esp_timer_create(&uptime_timer_args, &uptime_timer));
    ESP_ERROR_CHECK(esp_timer_start_periodic(uptime_timer, 1000000));  // 1 second

    // Start background tasks
    xTaskCreate(heartbeat_task, "heartbeat", 4096, NULL, 5, NULL);

    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "  System initialized successfully!");
    ESP_LOGI(TAG, "  Device ID: %s", g_app_state.device_id);
    ESP_LOGI(TAG, "  Backend URL: %s", g_app_state.backend_url);
    ESP_LOGI(TAG, "========================================");

    // Main loop
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));

        // Periodic status logging
        if (DEBUG_ENABLED && g_app_state.uptime_seconds % 60 == 0) {
            ESP_LOGI(TAG, "Status: WiFi=%d Backend=%d Camera=%d Display=%d Uptime=%lu",
                     g_app_state.wifi_connected,
                     g_app_state.backend_connected,
                     g_app_state.camera_ready,
                     g_app_state.display_ready,
                     g_app_state.uptime_seconds);
        }
    }
}
