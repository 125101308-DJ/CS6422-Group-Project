package com.project.dine.right.enums;

public enum CustomErrorCodes {
    SUCCESS("Success"),
    MISSING_REQUIRED_PARAMETER("A required parameter is missing."),
    UNAUTHORIZED("Unauthorized access"),
    EMPTY_JSON("An empty request was provided"),
    GENERIC_ERROR("General error");

    CustomErrorCodes(String description) {

    }
}