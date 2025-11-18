package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IMyReviewsService;
import com.project.dine.right.jdbc.models.MyReviews;
import com.project.dine.right.jdbc.repositories.MyReviewsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class MyReviewsService implements IMyReviewsService {

    @Autowired
    private MyReviewsRepository myReviewsRepository;

    @Override
    public List<MyReviews> findAllByUserId(Long userId) {
        return myReviewsRepository.findAllByUserId(userId);
    }

    @Override
    public MyReviews save(MyReviews myReviews) {
        return myReviewsRepository.save(myReviews);
    }

    @Override
    public Long countMyReviews() {
        return myReviewsRepository.count();
    }


}
