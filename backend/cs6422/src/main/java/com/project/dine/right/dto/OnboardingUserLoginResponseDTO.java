package com.project.dine.right.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class OnboardingUserLoginResponseDTO {

    private Long id;

    private String code;

    @Override
    public String toString() {
        return "OnboardingUserLoginResponseDTO{" +
                "id=" + id +
                '}';
    }
}
