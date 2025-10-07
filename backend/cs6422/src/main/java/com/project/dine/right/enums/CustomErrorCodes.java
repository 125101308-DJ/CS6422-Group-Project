package com.project.dine.right.enums;

public enum CustomErrorCodes {
    SUCCESS("Success"),
    MISSING_REQUIRED_PARAMETER("A required parameter is missing."),
    UNAUTHORIZED("Unauthorized access"),
    EMPTY_JSON("An empty request was provided"),
    GENERIC_ERROR("General error"),
    USER_ALREADY_EXISTS("User already exists"),
    INVALID_USER_ID("Invalid user id is given");

    CustomErrorCodes(String description) {

    }
}