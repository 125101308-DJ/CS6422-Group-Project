package com.project.dine.right.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@JsonInclude(JsonInclude.Include.NON_NULL)
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
