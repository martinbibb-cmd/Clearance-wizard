"""
OpenAPI specification for AR Engine API.

This module defines the OpenAPI/Swagger specification for automatic documentation.
"""

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "AR Engine API",
        "description": """REST API for AR marker detection and pose estimation. Supports AprilTag and ArUco markers with configurable parameters, session management, and calibration persistence.

## Production Deployment Notes

### Rate Limiting
The API enforces rate limiting (100 requests/minute per IP) to prevent abuse. When deployed behind a proxy or load balancer (e.g., Nginx, Cloudflare), ensure the `X-Forwarded-For` header is properly set to pass the client's real IP address. Without this header, all requests will appear to come from the proxy's IP and share the same rate limit.

Example Nginx configuration:
```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

### Security Guards
- Maximum payload size: 10 MB
- Maximum image dimensions: 4096x4096 pixels
- Rate limiting: 100 requests/minute per client IP
""",
        "version": "2.0.0",
        "contact": {
            "name": "AR Engine Team"
        },
        "license": {
            "name": "MIT"
        }
    },
    "servers": [
        {
            "url": "http://127.0.0.1:5000",
            "description": "Local development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ],
    "tags": [
        {
            "name": "health",
            "description": "Health check and status endpoints"
        },
        {
            "name": "configuration",
            "description": "Camera calibration configuration"
        },
        {
            "name": "detection",
            "description": "Marker detection endpoints"
        },
        {
            "name": "markers",
            "description": "Marker information and generation"
        }
    ],
    "components": {
        "schemas": {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "warnings": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional warning messages"
                    }
                },
                "required": ["error"]
            },
            "RateLimitError": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Rate limit exceeded"
                    },
                    "retry_after": {
                        "type": "integer",
                        "description": "Seconds to wait before retrying",
                        "example": 60
                    }
                },
                "required": ["error", "retry_after"]
            }
        },
        "responses": {
            "BadRequest": {
                "description": "Invalid request parameters",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"},
                        "examples": {
                            "missing_field": {
                                "value": {
                                    "error": "image field required"
                                }
                            },
                            "dimension_exceeded": {
                                "value": {
                                    "error": "Image dimensions exceed security limits",
                                    "warnings": ["Image dimensions 5000x5000 exceed maximum 4096x4096"]
                                }
                            }
                        }
                    }
                }
            },
            "PayloadTooLarge": {
                "description": "Payload exceeds maximum size limit",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"},
                        "example": {
                            "error": "Payload too large. Maximum size: 10485760 bytes"
                        }
                    }
                }
            },
            "RateLimitExceeded": {
                "description": "Rate limit exceeded",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/RateLimitError"},
                        "example": {
                            "error": "Rate limit exceeded",
                            "retry_after": 60
                        }
                    }
                }
            },
            "NotFound": {
                "description": "Resource not found",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"},
                        "example": {
                            "error": "Calibration not found"
                        }
                    }
                }
            },
            "InternalServerError": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Error"},
                        "example": {
                            "error": "Internal server error occurred"
                        }
                    }
                }
            }
        }
    },
    "paths": {
        "/health": {
            "get": {
                "tags": ["health"],
                "summary": "Health check",
                "description": "Check if the API is running and what features are available.",
                "responses": {
                    "200": {
                        "description": "API is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "ok"},
                                        "timestamp": {"type": "string", "format": "date-time"},
                                        "features": {
                                            "type": "object",
                                            "properties": {
                                                "apriltag": {"type": "boolean"},
                                                "aruco": {"type": "boolean"},
                                                "multipart_upload": {"type": "boolean"},
                                                "session_management": {"type": "boolean"},
                                                "calibration_persistence": {"type": "boolean"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/status": {
            "get": {
                "tags": ["health"],
                "summary": "Get API status",
                "description": "Get detailed API status including session and calibration information.",
                "parameters": [
                    {
                        "name": "session_id",
                        "in": "query",
                        "description": "Session ID to get specific session status",
                        "required": False,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Status information",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "timestamp": {"type": "string"},
                                        "active_sessions": {"type": "integer"},
                                        "stored_calibrations": {"type": "integer"},
                                        "features": {"type": "object"},
                                        "session": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/config": {
            "post": {
                "tags": ["configuration"],
                "summary": "Configure camera calibration",
                "description": "Setup camera calibration parameters (request-scoped). Returns session_id for subsequent requests.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["image_width", "image_height"],
                                "properties": {
                                    "image_width": {
                                        "type": "integer",
                                        "description": "Image width in pixels",
                                        "example": 1280
                                    },
                                    "image_height": {
                                        "type": "integer",
                                        "description": "Image height in pixels",
                                        "example": 720
                                    },
                                    "fov_degrees": {
                                        "type": "number",
                                        "description": "Vertical field of view in degrees",
                                        "default": 60.0
                                    },
                                    "dist_coeffs": {
                                        "type": "array",
                                        "items": {"type": "number"},
                                        "description": "Distortion coefficients [k1, k2, p1, p2, k3]",
                                        "default": [0, 0, 0, 0, 0]
                                    },
                                    "session_id": {
                                        "type": "string",
                                        "description": "Optional session ID to reuse existing session"
                                    },
                                    "device_name": {
                                        "type": "string",
                                        "description": "Device/camera name for calibration",
                                        "default": "unknown"
                                    },
                                    "save_calibration": {
                                        "type": "boolean",
                                        "description": "Save calibration for persistence",
                                        "default": False
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Calibration configured successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "session_id": {"type": "string"},
                                        "calibration_id": {"type": "string"},
                                        "camera_matrix": {
                                            "type": "array",
                                            "items": {
                                                "type": "array",
                                                "items": {"type": "number"}
                                            }
                                        },
                                        "dist_coeffs": {
                                            "type": "array",
                                            "items": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "429": {"$ref": "#/components/responses/RateLimitExceeded"},
                    "500": {"$ref": "#/components/responses/InternalServerError"}
                }
            }
        },
        "/api/v1/detect": {
            "post": {
                "tags": ["detection"],
                "summary": "Detect AR markers",
                "description": "Detect AR markers in an image. Supports both multipart/form-data and JSON (base64) uploads.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["image"],
                                "properties": {
                                    "image": {
                                        "type": "string",
                                        "description": "Base64-encoded image (JPEG or PNG)"
                                    },
                                    "marker_type": {
                                        "type": "string",
                                        "enum": ["apriltag", "aruco"],
                                        "default": "apriltag"
                                    },
                                    "marker_size": {
                                        "type": "number",
                                        "description": "Physical marker size in meters",
                                        "default": 0.19
                                    },
                                    "marker_count": {
                                        "type": "integer",
                                        "description": "Expected number of markers"
                                    },
                                    "tag_family": {
                                        "type": "string",
                                        "description": "AprilTag family",
                                        "default": "tag36h11"
                                    },
                                    "aruco_dict": {
                                        "type": "string",
                                        "description": "ArUco dictionary name",
                                        "default": "DICT_4X4_50"
                                    },
                                    "session_id": {
                                        "type": "string",
                                        "description": "Session ID from /config endpoint"
                                    },
                                    "calibration_id": {
                                        "type": "string",
                                        "description": "Calibration ID to use"
                                    }
                                }
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "required": ["image"],
                                "properties": {
                                    "image": {
                                        "type": "string",
                                        "format": "binary",
                                        "description": "Image file (JPEG or PNG)"
                                    },
                                    "marker_type": {
                                        "type": "string",
                                        "enum": ["apriltag", "aruco"]
                                    },
                                    "marker_size": {"type": "number"},
                                    "marker_count": {"type": "integer"},
                                    "tag_family": {"type": "string"},
                                    "aruco_dict": {"type": "string"},
                                    "session_id": {"type": "string"},
                                    "calibration_id": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Detection successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "markers": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "integer"},
                                                    "family": {"type": "string"},
                                                    "position": {
                                                        "type": "object",
                                                        "properties": {
                                                            "x": {"type": "number"},
                                                            "y": {"type": "number"},
                                                            "z": {"type": "number"}
                                                        }
                                                    },
                                                    "rotation_matrix": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "array",
                                                            "items": {"type": "number"}
                                                        }
                                                    },
                                                    "rvec": {
                                                        "type": "array",
                                                        "items": {"type": "number"},
                                                        "description": "Rotation vector"
                                                    },
                                                    "tvec": {
                                                        "type": "array",
                                                        "items": {"type": "number"},
                                                        "description": "Translation vector"
                                                    },
                                                    "transform_matrix": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "array",
                                                            "items": {"type": "number"}
                                                        },
                                                        "description": "4x4 transformation matrix"
                                                    },
                                                    "corners": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "array",
                                                            "items": {"type": "number"}
                                                        }
                                                    },
                                                    "confidence": {"type": "number"}
                                                }
                                            }
                                        },
                                        "marker_count": {"type": "integer"},
                                        "marker_type": {"type": "string"},
                                        "marker_size": {"type": "number"},
                                        "timings_ms": {
                                            "type": "object",
                                            "properties": {
                                                "image_decode_ms": {"type": "number"},
                                                "calibration_setup_ms": {"type": "number"},
                                                "detection_ms": {"type": "number"},
                                                "total_ms": {"type": "number"}
                                            }
                                        },
                                        "camera": {
                                            "type": "object",
                                            "properties": {
                                                "width": {"type": "integer"},
                                                "height": {"type": "integer"},
                                                "calibrated": {"type": "boolean"},
                                                "calibration_id": {"type": "string"}
                                            }
                                        },
                                        "warnings": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "session_id": {"type": "string"},
                                        "calibration_id": {"type": "string"},
                                        "timestamp": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "413": {"$ref": "#/components/responses/PayloadTooLarge"},
                    "429": {"$ref": "#/components/responses/RateLimitExceeded"},
                    "500": {"$ref": "#/components/responses/InternalServerError"}
                }
            }
        },
        "/api/v1/calibrations": {
            "get": {
                "tags": ["configuration"],
                "summary": "List calibrations",
                "description": "Get list of all stored calibrations.",
                "responses": {
                    "200": {
                        "description": "List of calibrations",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "calibrations": {
                                            "type": "array",
                                            "items": {"type": "object"}
                                        },
                                        "count": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/calibrations/{calibration_id}": {
            "get": {
                "tags": ["configuration"],
                "summary": "Get calibration by ID",
                "description": "Get specific calibration data by calibration ID.",
                "parameters": [
                    {
                        "name": "calibration_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Calibration data",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    },
                    "404": {"$ref": "#/components/responses/NotFound"}
                }
            }
        },
        "/api/v1/supported_markers": {
            "get": {
                "tags": ["markers"],
                "summary": "Get supported markers",
                "description": "Get list of all supported marker types and their options.",
                "responses": {
                    "200": {
                        "description": "Supported markers",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "marker_types": {
                                            "type": "object",
                                            "properties": {
                                                "apriltag": {"type": "object"},
                                                "aruco": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/generate_marker": {
            "post": {
                "tags": ["markers"],
                "summary": "Generate marker image",
                "description": "Generate a marker image (ArUco only).",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["marker_type", "marker_id"],
                                "properties": {
                                    "marker_type": {
                                        "type": "string",
                                        "enum": ["aruco"]
                                    },
                                    "marker_id": {"type": "integer"},
                                    "size_pixels": {
                                        "type": "integer",
                                        "default": 400
                                    },
                                    "aruco_dict": {
                                        "type": "string",
                                        "default": "DICT_4X4_50"
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Marker image",
                        "content": {
                            "image/png": {
                                "schema": {
                                    "type": "string",
                                    "format": "binary"
                                }
                            }
                        }
                    },
                    "400": {"$ref": "#/components/responses/BadRequest"},
                    "501": {
                        "description": "Not implemented",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"},
                                "example": {
                                    "error": "AprilTag generation not yet implemented. Use in-app generator."
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
