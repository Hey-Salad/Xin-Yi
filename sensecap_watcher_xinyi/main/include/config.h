/**
 * @file config.h
 * @brief Configuration header for SenseCAP Watcher Xin-Yi Firmware
 *
 * Based on heysalad_xiao_og Config.h but adapted for SenseCAP Watcher hardware
 * and Xin-Yi system integration
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>
#include <stdbool.h>

// =============================================================================
// FIRMWARE VERSION
// =============================================================================
#define FIRMWARE_VERSION "1.0.0-xinyi"
#define DEVICE_TYPE "sensecap-watcher"
#define DEVICE_NAME "XinYi-Watcher"

// =============================================================================
// XIN-YI BACKEND CONFIGURATION
// =============================================================================
// Production server (recommended)
#define XINYI_API_URL "https://wms.heysalad.app"

// Or use local Raspberry Pi server (same WiFi only)
// #define XINYI_API_URL "http://192.168.1.130:2124"

#define XINYI_API_REGISTER "/api/devices/register"
#define XINYI_API_STATUS "/api/devices/%s/status"
#define XINYI_API_COMMAND "/api/devices/%s/command"
#define XINYI_WEBSOCKET_URL "wss://wms.heysalad.app/ws/devices/%s"

// Device will auto-register with backend on first boot
#define AUTO_REGISTER_ENABLED true

// =============================================================================
// WIFI CONFIGURATION
// =============================================================================
#define WIFI_SSID_DEFAULT ""  // Will use AP mode if empty
#define WIFI_PASSWORD_DEFAULT ""

// Access Point mode (when no WiFi configured)
#define AP_SSID "XinYi-Watcher"
#define AP_PASSWORD "xinyi2024"
#define AP_CHANNEL 6
#define AP_MAX_CONNECTIONS 4

// WiFi retry settings
#define WIFI_MAXIMUM_RETRY 5
#define WIFI_RETRY_DELAY_MS 5000

// =============================================================================
// SENSECAP WATCHER HARDWARE PINS
// =============================================================================

// Display (412x412 QSPI LCD - SPI3_HOST)
#define LCD_WIDTH 412
#define LCD_HEIGHT 412
#define LCD_SPI_HOST SPI3_HOST
#define LCD_PIXEL_CLOCK_HZ (40 * 1000 * 1000)  // 40MHz
#define LCD_PIN_NUM_MOSI 11
#define LCD_PIN_NUM_CLK 12
#define LCD_PIN_NUM_CS 10
#define LCD_PIN_NUM_DC 13
#define LCD_PIN_NUM_RST 14
#define LCD_PIN_NUM_BL 2   // Backlight (via IO expander usually)

// Touchscreen (I2C)
#define TOUCH_I2C_NUM I2C_NUM_1
#define TOUCH_PIN_SDA 39
#define TOUCH_PIN_SCL 38
#define TOUCH_I2C_FREQ_HZ 400000

// Audio Codec (Dual: ES8311 + ES7243E)
#define AUDIO_I2S_NUM I2S_NUM_0
#define AUDIO_SAMPLE_RATE 24000
#define AUDIO_PIN_MCLK 10
#define AUDIO_PIN_WS 12
#define AUDIO_PIN_BCLK 11
#define AUDIO_PIN_DIN 15   // Speaker
#define AUDIO_PIN_DOUT 16  // Microphone

// Himax Vision AI Processor (SPI2_HOST via IO expander)
#define HIMAX_SPI_HOST SPI2_HOST
#define HIMAX_PIN_CS 42
#define HIMAX_PIN_INT 41

// IO Expander (TCA9555 or similar)
#define IO_EXPANDER_I2C_ADDR 0x20

// Battery ADC
#define BATTERY_ADC_CHANNEL ADC1_CHANNEL_0
#define BATTERY_ADC_ATTEN ADC_ATTEN_DB_11

// SD Card (if present)
#define SD_CARD_PIN_CMD 35
#define SD_CARD_PIN_CLK 36
#define SD_CARD_PIN_D0 37

// Rotary Encoder
#define ENCODER_PIN_A 40
#define ENCODER_PIN_B 41
#define ENCODER_PIN_BTN 42

// =============================================================================
// HTTP SERVER CONFIGURATION
// =============================================================================
#define HTTP_SERVER_PORT 80
#define HTTP_MAX_URI_LEN 512
#define HTTP_MAX_HEADER_LEN 1024
#define WEBSOCKET_MAX_PAYLOAD 4096

// Session timeout (seconds)
#define SESSION_TIMEOUT_SEC 3600

// Default admin password (CHANGE THIS!)
#define DEFAULT_AUTH_PASSWORD "xinyi2024"

// =============================================================================
// CAMERA / STREAMING CONFIGURATION
// =============================================================================
#define CAMERA_ENABLED true
#define CAMERA_FRAME_SIZE FRAMESIZE_VGA  // 640x480 via Himax
#define CAMERA_PIXEL_FORMAT PIXFORMAT_JPEG
#define CAMERA_JPEG_QUALITY 12

// WebSocket streaming
#define STREAM_FRAME_INTERVAL_MS 100  // 10 FPS
#define STREAM_MAX_CLIENTS 3

// Photo capture settings
#define CAPTURE_QUALITY 8  // Higher quality for photo capture

// =============================================================================
// DISPLAY CONFIGURATION
// =============================================================================
#define DISPLAY_ENABLED true
#define DISPLAY_ROTATION 0  // 0, 90, 180, 270
#define DISPLAY_BRIGHTNESS 80  // 0-100%

// UI Colors (RGB565 format)
#define COLOR_BACKGROUND 0x0000   // Black
#define COLOR_PRIMARY 0xED4C     // Cherry Red (#ed4c4c from Laura dashboard)
#define COLOR_TEXT 0xFFFF        // White
#define COLOR_SUCCESS 0x07E0     // Green
#define COLOR_ERROR 0xF800       // Red
#define COLOR_WARNING 0xFFE0     // Yellow

// Font sizes
#define FONT_SIZE_SMALL 16
#define FONT_SIZE_MEDIUM 24
#define FONT_SIZE_LARGE 32
#define FONT_SIZE_XLARGE 48

// =============================================================================
// BLUETOOTH CONFIGURATION
// =============================================================================
#define BLE_ENABLED true
#define BLE_DEVICE_NAME "XinYi-Watcher"
#define BLE_SERVICE_UUID "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define BLE_RX_CHAR_UUID "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define BLE_TX_CHAR_UUID "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

// =============================================================================
// STATUS UPDATE INTERVALS
// =============================================================================
#define STATUS_BROADCAST_INTERVAL_MS 5000      // WebSocket status updates
#define BACKEND_HEARTBEAT_INTERVAL_MS 30000    // Xin-Yi backend heartbeat
#define BATTERY_CHECK_INTERVAL_MS 60000        // Battery level check

// =============================================================================
// STORAGE CONFIGURATION
// =============================================================================
#define SPIFFS_BASE_PATH "/spiffs"
#define SPIFFS_MAX_FILES 10

// Asset paths (similar to heysalad_xiao_og)
#define ASSET_LOGO_PATH "/spiffs/assets/logo.png"
#define ASSET_ICON_IDLE "/spiffs/assets/idle.png"
#define ASSET_ICON_ACTIVE "/spiffs/assets/active.png"
#define ASSET_ICON_ERROR "/spiffs/assets/error.png"

// =============================================================================
// FEATURE FLAGS
// =============================================================================
#define FEATURE_VOICE_WAKEUP false     // Future: integrate with XiaoZhi
#define FEATURE_AI_VISION true          // Use Himax processor
#define FEATURE_BARCODE_SCAN true       // For warehouse operations
#define FEATURE_DOCUMENT_CAPTURE true   // For delivery receipts
#define FEATURE_GPS false               // SenseCAP doesn't have GPS
#define FEATURE_OTA_UPDATES true        // Over-the-air firmware updates

// =============================================================================
// XIN-YI SPECIFIC SETTINGS
// =============================================================================

// Device roles (what this device will be used for)
typedef enum {
    ROLE_WAREHOUSE_TERMINAL,   // Fixed terminal in warehouse
    ROLE_MOBILE_SCANNER,       // Mobile handheld scanner
    ROLE_DELIVERY_CONFIRM,     // Delivery confirmation device
    ROLE_INVENTORY_CHECKER     // Inventory checking device
} device_role_t;

#define DEFAULT_DEVICE_ROLE ROLE_WAREHOUSE_TERMINAL

// Auto-capture modes
#define AUTO_CAPTURE_ENABLED false
#define AUTO_CAPTURE_INTERVAL_MS 10000

// =============================================================================
// DEBUGGING
// =============================================================================
#define DEBUG_ENABLED true
#define LOG_TO_SERIAL true
#define LOG_TO_SPIFFS false

#if DEBUG_ENABLED
#define DEBUG_LOG(fmt, ...) printf("[DEBUG] " fmt "\n", ##__VA_ARGS__)
#else
#define DEBUG_LOG(fmt, ...)
#endif

#endif // CONFIG_H
