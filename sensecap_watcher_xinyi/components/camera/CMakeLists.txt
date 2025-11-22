idf_component_register(
    SRCS "camera_stub.c"
    INCLUDE_DIRS "."
    REQUIRES driver esp_timer log shared
)
