package com.project.dine.right.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@JsonInclude(JsonInclude.Include.NON_NULL)
public class OnboardingUserSignupResponseDTO {

    private String code;

    private Long id;

}
