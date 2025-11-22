/**
 * @file http_server.c
 * @brief Minimal HTTP server to expose device status and basic endpoints.
 */

#include "http_server.h"

#include <stdio.h>
#include <string.h>

#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_err.h"

static const char *TAG = "HTTP_SERVER";
static httpd_handle_t server = NULL;
static app_state_t *state_context = NULL;

static esp_err_t status_get_handler(httpd_req_t *req)
{
    if (!state_context) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "state missing");
    }

    char buffer[256];
    int len = snprintf(buffer, sizeof(buffer),
                       "{\"device_id\":\"%s\",\"wifi_connected\":%d,\"backend_connected\":%d,"
                       "\"camera_ready\":%d,\"display_ready\":%d,\"uptime_seconds\":%lu}",
                       state_context->device_id,
                       state_context->wifi_connected,
                       state_context->backend_connected,
                       state_context->camera_ready,
                       state_context->display_ready,
                       state_context->uptime_seconds);

    httpd_resp_set_type(req, "application/json");
    return httpd_resp_send(req, buffer, len);
}

static esp_err_t root_get_handler(httpd_req_t *req)
{
    const char response[] =
        "<html><head><title>SenseCAP Watcher</title></head>"
        "<body><h2>XinYi SenseCAP Watcher</h2>"
        "<p>Status: Up and running</p>"
        "</body></html>";

    httpd_resp_set_type(req, "text/html");
    return httpd_resp_send(req, response, sizeof(response) - 1);
}

static esp_err_t settings_post_handler(httpd_req_t *req)
{
    char buffer[128] = {0};
    int len = httpd_req_recv(req, buffer, sizeof(buffer) - 1);
    if (len > 0) {
        ESP_LOGI(TAG, "Settings received: %.*s", len, buffer);
    }
    httpd_resp_set_type(req, "application/json");
    return httpd_resp_send(req, "{\"status\":\"ok\"}", HTTPD_RESP_USE_STRLEN);
}

void http_server_init(app_state_t *state)
{
    if (server != NULL) {
        ESP_LOGW(TAG, "HTTP server already running");
        return;
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.max_uri_handlers = 6;
    config.server_port = HTTP_SERVER_PORT;

    state_context = state;

    httpd_uri_t root = {
        .uri = "/",
        .method = HTTP_GET,
        .handler = root_get_handler,
        .user_ctx = state
    };

    httpd_uri_t status = {
        .uri = "/api/status",
        .method = HTTP_GET,
        .handler = status_get_handler,
        .user_ctx = state
    };

    httpd_uri_t settings = {
        .uri = "/api/settings",
        .method = HTTP_POST,
        .handler = settings_post_handler,
        .user_ctx = state
    };

    esp_err_t err = httpd_start(&server, &config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Failed to start HTTP server: %s", esp_err_to_name(err));
        state->backend_connected = false;
        return;
    }

    httpd_register_uri_handler(server, &root);
    httpd_register_uri_handler(server, &status);
    httpd_register_uri_handler(server, &settings);

    ESP_LOGI(TAG, "HTTP server started on port %d", config.server_port);
    state->backend_connected = true;
}
