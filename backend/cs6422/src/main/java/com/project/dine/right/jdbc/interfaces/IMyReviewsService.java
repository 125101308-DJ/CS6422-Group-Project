package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.MyReviews;

import java.util.List;

public interface IMyReviewsService {

    List<MyReviews> findAllByUserId(Long userId);

    MyReviews save(MyReviews myReviews);

    Long countMyReviews();

}
