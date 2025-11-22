/**
 * @file http_server.h
 * @brief HTTP server setup for the SenseCAP web dashboard.
 */

#ifndef HTTP_SERVER_H
#define HTTP_SERVER_H

#include "app_state.h"

#ifdef __cplusplus
extern "C" {
#endif

void http_server_init(app_state_t *state);

#ifdef __cplusplus
}
#endif

#endif // HTTP_SERVER_H
