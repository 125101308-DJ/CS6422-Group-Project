package com.project.dine.right.controller;

import com.project.dine.right.dto.DashboardRestaurantsDataResponseDTO;
import com.project.dine.right.dto.DashboardUserInfoResponseDTO;
import com.project.dine.right.enums.CustomErrorCodes;
import com.project.dine.right.interfaces.IDashboardService;
import com.project.dine.right.utils.UserDataUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.util.ObjectUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DashboardController {

    @Autowired
    private UserDataUtils USER_DATA_UTILS;

    @Autowired
    private IDashboardService dashboardService;

    @GetMapping("/getAllRestaurantsData")
    public ResponseEntity<DashboardRestaurantsDataResponseDTO> getRestaurantsData() {

        var responseDTO = new DashboardRestaurantsDataResponseDTO();

        var restaurants = dashboardService.getRestaurants();

        responseDTO.setRestaurantData(restaurants);
        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @GetMapping("/getUserInfo")
    public ResponseEntity<DashboardUserInfoResponseDTO> getUserInfo(@RequestParam("userId") Long userId) {

        var responseDTO = new DashboardUserInfoResponseDTO();

        if (ObjectUtils.isEmpty(userId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!USER_DATA_UTILS.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userVO = dashboardService.getMyUser(userId);
        var myWishList = dashboardService.getWishlistRestaurants(userId);
        var topKRestaurants = dashboardService.getTopKRestaurants(userId);

        responseDTO.setUser(userVO);
        responseDTO.setWishlistRestaurants(myWishList);
        responseDTO.setTopKRestaurants(topKRestaurants);

        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }
}
