package com.project.dine.right.controller;

import com.project.dine.right.interfaces.IOnboardingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class OnboardingController {

    @Autowired
    IOnboardingService onboardingService;

    @RequestMapping("/login")
    public int userLogin(HttpHeaders headers, String email, String password) {

        if (!StringUtils.hasLength(email) || !StringUtils.hasLength(password)) {
            return HttpStatus.BAD_REQUEST.value();
        }

        if (onboardingService.userLogin(email, password)) {
            return HttpStatus.OK.value();
        }

        return HttpStatus.UNAUTHORIZED.value();
    }

}
