package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.UserReviews;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserReviewsRepository extends CrudRepository<UserReviews, Long> {

    @Query("select * from public.user_reviews where place_id=:placeId")
    List<UserReviews> findAllByPlaceId(@Param("placeId") Long placeId);
}
