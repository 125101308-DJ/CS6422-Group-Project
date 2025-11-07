package com.project.dine.right.controller;

import com.project.dine.right.dto.RestaurantPageAddReviewRequestDTO;
import com.project.dine.right.dto.RestaurantPageAddReviewResponseDTO;
import com.project.dine.right.enums.CustomErrorCodes;
import com.project.dine.right.services.RestaurantPageService;
import com.project.dine.right.utils.UserDataUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.util.ObjectUtils;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RestaurantPageController {

    @Autowired
    private UserDataUtils userDataUtils;

    @Autowired
    private RestaurantPageService restaurantPageService;

    @PostMapping("/addReview")
    public ResponseEntity<RestaurantPageAddReviewResponseDTO> addReview(@RequestBody(required = false) RestaurantPageAddReviewRequestDTO restaurantPageAddReviewRequestDTO) {

        var responseDTO = new RestaurantPageAddReviewResponseDTO();

        //Early detection on existence of request body
        if (ObjectUtils.isEmpty(restaurantPageAddReviewRequestDTO)) {
            responseDTO.setCode(CustomErrorCodes.EMPTY_JSON.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        var userId = restaurantPageAddReviewRequestDTO.getUserId();
        var placeId = restaurantPageAddReviewRequestDTO.getRestaurantId();

        //Early detection on existence of userId
        if (ObjectUtils.isEmpty(userId) || ObjectUtils.isEmpty(placeId)) {
            responseDTO.setCode(CustomErrorCodes.MISSING_REQUIRED_PARAMETER.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserExists(userId)) {
            responseDTO.setCode(CustomErrorCodes.USER_DOES_NOT_EXISTS.name());
            return ResponseEntity.badRequest().body(responseDTO);
        }

        if (!userDataUtils.checkIfUserNeverReviewed(userId, placeId)) {
            responseDTO.setCode(CustomErrorCodes.ALREADY_REVIEWED_CURRENT_RESTAURANT.name());
            return ResponseEntity.ok().body(responseDTO);
        }

        restaurantPageService.saveReview(restaurantPageAddReviewRequestDTO);

        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }

}
