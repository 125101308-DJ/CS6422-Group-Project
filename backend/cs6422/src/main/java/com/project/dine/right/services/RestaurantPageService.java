package com.project.dine.right.services;

import com.project.dine.right.dto.RestaurantPageAddReviewRequestDTO;
import com.project.dine.right.jdbc.interfaces.IMyReviewsService;
import com.project.dine.right.jdbc.interfaces.IRestaurantDataService;
import com.project.dine.right.jdbc.interfaces.IUserDataService;
import com.project.dine.right.jdbc.interfaces.IUserReviewsService;
import com.project.dine.right.jdbc.models.MyReviews;
import com.project.dine.right.jdbc.models.UserReviews;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.text.SimpleDateFormat;
import java.util.Date;

@Service
public class RestaurantPageService {

    @Autowired
    IMyReviewsService myReviewsService;

    @Autowired
    IRestaurantDataService restaurantDataService;

    @Autowired
    IUserDataService userDataService;

    @Autowired
    IUserReviewsService userReviewsService;

    public void saveReview(RestaurantPageAddReviewRequestDTO restaurantPageAddReviewRequestDTO) {

        String date = new SimpleDateFormat("yyyy-MM-dd").format(new Date());

        var userReview = new UserReviews();

        userReview.setPlaceId(restaurantPageAddReviewRequestDTO.getRestaurantId());
        userReview.setRestaurantName(restaurantDataService.findByRestaurantId(restaurantPageAddReviewRequestDTO.getRestaurantId()).getName());
        userReview.setUsername(userDataService.getUserDataById(restaurantPageAddReviewRequestDTO.getUserId()).get().getName());
        userReview.setReviewText(restaurantPageAddReviewRequestDTO.getComment());
        userReview.setRating(restaurantPageAddReviewRequestDTO.getUserRating().shortValue());
        userReview.setReviewDate(date);

        userReviewsService.save(userReview);

        var myReview = new MyReviews();

        myReview.setUserId(restaurantPageAddReviewRequestDTO.getUserId());
        myReview.setPlaceId(restaurantPageAddReviewRequestDTO.getRestaurantId());
        myReview.setRating(restaurantPageAddReviewRequestDTO.getUserRating().shortValue());
        myReview.setReviewText(restaurantPageAddReviewRequestDTO.getComment());
        myReview.setReviewDate(date);

        myReviewsService.save(myReview);
    }

}
