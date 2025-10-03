package com.project.dine.right.dto;

import lombok.Setter;

public class OnboardingUserLoginResponseDTO {

    @Setter
    private Long id;

    @Setter
    private String code;

    @Override
    public String toString() {
        return "OnboardingUserLoginResponseDTO{" +
                "id=" + id +
                '}';
    }
}
