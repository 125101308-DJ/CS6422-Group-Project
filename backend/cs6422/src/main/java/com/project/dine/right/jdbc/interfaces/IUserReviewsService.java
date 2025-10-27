package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.UserReviews;

import java.util.List;

public interface IUserReviewsService {

    List<UserReviews> findAllByPlaceId(Long placeId);

}
