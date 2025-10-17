package com.project.dine.right.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
public class OnboardingUserSignupRequestDTO {

    private String name;

    private String email;

    private String password;

}
