package com.project.dine.right.services;

import com.project.dine.right.dto.RestaurantPageAddReviewRequestDTO;
import com.project.dine.right.jdbc.interfaces.IMyReviewsService;
import com.project.dine.right.jdbc.models.MyReviews;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.text.SimpleDateFormat;
import java.util.Date;

@Service
public class RestaurantPageService {

    @Autowired
    IMyReviewsService myReviewsService;

    public void saveReview(RestaurantPageAddReviewRequestDTO restaurantPageAddReviewRequestDTO) {

        var myReview = new MyReviews();

        myReview.setUserId(restaurantPageAddReviewRequestDTO.getUserId());
        myReview.setPlaceId(restaurantPageAddReviewRequestDTO.getRestaurantId());
        myReview.setRating(restaurantPageAddReviewRequestDTO.getUserRating().shortValue());
        myReview.setReviewText(restaurantPageAddReviewRequestDTO.getComment());
        myReview.setReviewDate(new SimpleDateFormat("yyyy-MM-dd").format(new Date()));

        myReviewsService.save(myReview);
    }

}
