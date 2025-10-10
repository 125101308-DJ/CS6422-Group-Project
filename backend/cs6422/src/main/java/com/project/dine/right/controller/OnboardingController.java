package com.project.dine.right.controller;

import com.project.dine.right.dto.*;
import com.project.dine.right.enums.CustomErrorCodes;
import com.project.dine.right.interfaces.IOnboardingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.util.ObjectUtils;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class OnboardingController {

    @Autowired
    IOnboardingService onboardingService;

    @GetMapping("/login")
    public ResponseEntity<OnboardingUserLoginResponseDTO> userLogin(@RequestBody(required = false) OnboardingUserLoginRequestDTO onboardingUserLoginRequestDTO) {

        var responseDTO = new OnboardingUserLoginResponseDTO();

        //Early detection on existence of request body
        if (ObjectUtils.isEmpty(onboardingUserLoginRequestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var email = onboardingUserLoginRequestDTO.getEmail();
        var password = onboardingUserLoginRequestDTO.getPassword();

        //Early detection on existence of either email or password strings
        if (!StringUtils.hasLength(email) || !StringUtils.hasLength(password)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        //Service function to check if user exists
        var userData = onboardingService.userLogin(email, password);
        if (!ObjectUtils.isEmpty(userData)) {

            responseDTO.setId(userData.getUserId());
            responseDTO.setCode(CustomErrorCodes.SUCCESS.name());

            return ResponseEntity.ok().body(responseDTO);
        }

        responseDTO.setCode(CustomErrorCodes.UNAUTHORIZED.name());
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(responseDTO);
    }

    @PostMapping("/signup")
    public ResponseEntity<OnboardingUserSignupResponseDTO> userSignup(@RequestBody(required = false) OnboardingUserSignupRequestDTO onboardingUserSignupRequestDTO) {

        var responseDTO = new OnboardingUserSignupResponseDTO();

        //Early detection on existence of request body
        if (ObjectUtils.isEmpty(onboardingUserSignupRequestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var name = onboardingUserSignupRequestDTO.getName();
        var email = onboardingUserSignupRequestDTO.getEmail();
        var password = onboardingUserSignupRequestDTO.getPassword();

        //Early detection on existence of either email or password strings
        if (!StringUtils.hasLength(email) || !StringUtils.hasLength(password) || !StringUtils.hasLength(name)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (onboardingService.checkIfUserExists(email)) {
            responseDTO.setCode(CustomErrorCodes.USER_ALREADY_EXISTS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        var userData = onboardingService.saveUser(name, email, password);
        if (!ObjectUtils.isEmpty(userData)) {
            responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
            responseDTO.setId(userData.getUserId());
            return ResponseEntity.ok().body(responseDTO);
        }

        responseDTO.setCode(CustomErrorCodes.GENERIC_ERROR.name());
        return ResponseEntity.badRequest().body(responseDTO);
    }

    @PostMapping("/savePrefs")
    public ResponseEntity<OnboardingUserSavePreferenceResponseDTO> userSavePreferences(@RequestBody(required = false) OnboardingUserSavePreferenceRequestDTO onboardingUserSavePreferenceRequestDTO) {

        var responseDTO = new OnboardingUserSavePreferenceResponseDTO();

        //Early detection on existence of request body
        if (ObjectUtils.isEmpty(onboardingUserSavePreferenceRequestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = onboardingUserSavePreferenceRequestDTO.getUserId();

        if (ObjectUtils.isEmpty(userId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!onboardingService.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var preferences = onboardingUserSavePreferenceRequestDTO.getPreferenceObject();

        if (!ObjectUtils.isEmpty(preferences)) {

            var ambience = preferences.getAmbience();

            if (!ambience.isEmpty()) {
                onboardingService.saveAmbienceData(ambience, userId);
            }

            var cuisines = preferences.getCuisines();

            if (!cuisines.isEmpty()) {
                onboardingService.saveCuisinesData(cuisines, userId);
            }

            var priceRange = preferences.getPriceRange();
            var location = preferences.getLocation();
            var service = preferences.getService();

            onboardingService.saveOtherPreferences(priceRange, location, service, userId);

            responseDTO.setId(userId);
            responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        responseDTO.setCode(CustomErrorCodes.GENERIC_ERROR.name());
        return ResponseEntity.badRequest().body(responseDTO);
    }

}
