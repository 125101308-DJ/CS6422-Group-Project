package com.project.dine.right.controller;

import com.project.dine.right.dto.OnboardingUserLoginRequestDTO;
import com.project.dine.right.interfaces.IOnboardingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.ObjectUtils;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class OnboardingController {

    @Autowired
    IOnboardingService onboardingService;

    @RequestMapping("/login")
    public ResponseEntity userLogin(@RequestBody OnboardingUserLoginRequestDTO onboardingUserLoginRequestDTO) {

        //Early detection on existence of request body
        if (ObjectUtils.isEmpty(onboardingUserLoginRequestDTO)) {
            return ResponseEntity.badRequest().build();
        }

        var email = onboardingUserLoginRequestDTO.getEmail();
        var password = onboardingUserLoginRequestDTO.getPassword();

        //Early detection on existence of either email or password strings
        if (!StringUtils.hasLength(email) || !StringUtils.hasLength(password)) {
            return ResponseEntity.badRequest().build();
        }

        //Service function to check if user exists
        if (onboardingService.userLogin(email, password)) {
            return ResponseEntity.ok().build();
        }

        return ResponseEntity.status(HttpStatus.UNAUTHORIZED.value()).build();
    }

}
