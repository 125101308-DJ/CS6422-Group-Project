package com.project.dine.right.controller;

import com.project.dine.right.dto.*;
import com.project.dine.right.enums.CustomErrorCodes;
import com.project.dine.right.interfaces.IDashboardService;
import com.project.dine.right.utils.UserDataUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.util.ObjectUtils;
import org.springframework.web.bind.annotation.*;

import java.util.Collections;

@RestController
public class DashboardController {

    @Autowired
    private UserDataUtils userDataUtils;

    @Autowired
    private IDashboardService dashboardService;

    @GetMapping("/getAllRestaurantsData")
    public ResponseEntity<DashboardRestaurantsDataResponseDTO> getRestaurantsData() {

        var responseDTO = new DashboardRestaurantsDataResponseDTO();

        var restaurants = dashboardService.getRestaurants();

        responseDTO.setRestaurants(restaurants);
        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @GetMapping("/getRestaurantsDataById/{id}")
    public ResponseEntity<DashboardRestaurantsDataResponseDTO> getRestaurantsDataById(@PathVariable("id") Long id) {

        var responseDTO = new DashboardRestaurantsDataResponseDTO();

        var restaurants = dashboardService.getRestaurantById(id);

        responseDTO.setRestaurants(Collections.singletonList(restaurants));
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

        if (!userDataUtils.checkIfUserExists(userId)) {
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

    @GetMapping("/getRecommendations/{userId}")
    public ResponseEntity<DashboardRecommendationsResponseDTO> getRecommendations(@PathVariable("userId") Long userId) {

        var responseDTO = new DashboardRecommendationsResponseDTO();

        if (ObjectUtils.isEmpty(userId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var recommendations = dashboardService.getRecommendedRestaurants(userId);

        responseDTO.setRecommendedRestaurants(recommendations);
        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @GetMapping("/getUserMetrics")
    public ResponseEntity<DashboardUserMetricsResponseDTO> getUserMetrics(@RequestParam("userId") Long userId) {

        var responseDTO = new DashboardUserMetricsResponseDTO();

        if (ObjectUtils.isEmpty(userId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var countDetails = dashboardService.getCountDetails(userId);

        responseDTO.setCountDetails(countDetails);
        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);

    }

    @PostMapping("/getUserWishlist")
    public ResponseEntity<DashboardGetUserWishlistResponseDTO> getUserWishlist(@RequestBody(required = false) DashboardGenericGetByUserIdRequestDTO requestDTO) {

        var responseDTO = new DashboardGetUserWishlistResponseDTO();

        if (ObjectUtils.isEmpty(requestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = requestDTO.getUserId();

        if (ObjectUtils.isEmpty(userId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        var wishlist = dashboardService.getUserWishlist(userId);

        responseDTO.setWishlist(wishlist);
        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @PostMapping("/getUserReviewsWritten")
    public ResponseEntity<DashboardGetUserReviewsResponseDTO> getUserReviewsWritten(@RequestBody(required = false) DashboardGenericGetByUserIdRequestDTO requestDTO) {

        var responseDTO = new DashboardGetUserReviewsResponseDTO();

        if (ObjectUtils.isEmpty(requestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = requestDTO.getUserId();

        if (ObjectUtils.isEmpty(userId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        var reviews = dashboardService.getUserReviewsWritten(userId);

        responseDTO.setReviewsWritten(reviews);
        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @PostMapping("/getUserRestaurantsVisited")
    public ResponseEntity<DashboardGetUserVisitedResponseDTO> getUserRestaurantsVisited(@RequestBody(required = false) DashboardGenericGetByUserIdRequestDTO requestDTO) {

        var responseDTO = new DashboardGetUserVisitedResponseDTO();

        if (ObjectUtils.isEmpty(requestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = requestDTO.getUserId();

        if (ObjectUtils.isEmpty(userId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        var visited = dashboardService.getUserVisited(userId);

        responseDTO.setRestaurantsVisited(visited);
        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @PostMapping("/addWishlistRestaurant")
    public ResponseEntity<GenericCodeOnlyResponseDTO> addWishlistRestaurant(@RequestBody(required = false) DashboardGenericUserIdAndRestaurantIdRequestDTO requestDTO) {

        var responseDTO = new GenericCodeOnlyResponseDTO();

        if (ObjectUtils.isEmpty(requestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = requestDTO.getUserId();
        var restaurantId = requestDTO.getRestaurantId();

        if (ObjectUtils.isEmpty(userId) || ObjectUtils.isEmpty(restaurantId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        dashboardService.addToUserWishlist(userId, restaurantId);

        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @DeleteMapping("/removeWishlistRestaurant")
    public ResponseEntity<GenericCodeOnlyResponseDTO> removeWishlistRestaurant(@RequestBody(required = false) DashboardGenericUserIdAndRestaurantIdRequestDTO requestDTO) {

        var responseDTO = new GenericCodeOnlyResponseDTO();

        if (ObjectUtils.isEmpty(requestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = requestDTO.getUserId();
        var restaurantId = requestDTO.getRestaurantId();

        if (ObjectUtils.isEmpty(userId) || ObjectUtils.isEmpty(restaurantId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        dashboardService.removeToUserWishlist(userId, restaurantId);

        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @PostMapping("/addVisitedRestaurant")
    public ResponseEntity<GenericCodeOnlyResponseDTO> addVisitedRestaurant(@RequestBody(required = false) DashboardGenericUserIdAndRestaurantIdRequestDTO requestDTO) {

        var responseDTO = new GenericCodeOnlyResponseDTO();

        if (ObjectUtils.isEmpty(requestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = requestDTO.getUserId();
        var restaurantId = requestDTO.getRestaurantId();

        if (ObjectUtils.isEmpty(userId) || ObjectUtils.isEmpty(restaurantId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        dashboardService.addToVisited(userId, restaurantId);

        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

    @DeleteMapping("/removeVisitedRestaurant")
    public ResponseEntity<GenericCodeOnlyResponseDTO> removeVisitedRestaurant(@RequestBody(required = false) DashboardGenericUserIdAndRestaurantIdRequestDTO requestDTO) {

        var responseDTO = new GenericCodeOnlyResponseDTO();

        if (ObjectUtils.isEmpty(requestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = requestDTO.getUserId();
        var restaurantId = requestDTO.getRestaurantId();

        if (ObjectUtils.isEmpty(userId) || ObjectUtils.isEmpty(restaurantId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        dashboardService.removeVisited(userId, restaurantId);

        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }
}
