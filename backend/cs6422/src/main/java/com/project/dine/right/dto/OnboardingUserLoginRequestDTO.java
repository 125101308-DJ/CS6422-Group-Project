package com.project.dine.right.dto;

import lombok.Getter;

public class OnboardingUserLoginRequestDTO {

    @Getter
    private String email;

    @Getter
    private String password;

    @Override
    public String toString() {
        return "OnboardingUserLoginRequestDTO{" +
                "email='" + email + '\'' +
                ", password='" + password + '\'' +
                '}';
    }
}
