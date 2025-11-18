package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IUserReviewsService;
import com.project.dine.right.jdbc.models.UserReviews;
import com.project.dine.right.jdbc.repositories.UserReviewsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserReviewsService implements IUserReviewsService {

    @Autowired
    private UserReviewsRepository userReviewsRepository;

    @Override
    public List<UserReviews> findAllByPlaceId(Long placeId) {
        return userReviewsRepository.findAllByPlaceId(placeId);
    }

    @Override
    public void save(UserReviews userReview) {
        userReviewsRepository.save(userReview);
    }
}
