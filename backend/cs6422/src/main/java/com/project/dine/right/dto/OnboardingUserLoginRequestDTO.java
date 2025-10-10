package com.project.dine.right.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class OnboardingUserLoginRequestDTO {

    private String email;

    private String password;

    @Override
    public String toString() {
        return "OnboardingUserLoginRequestDTO{" +
                "email='" + email + '\'' +
                ", password='" + password + '\'' +
                '}';
    }
}
