package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.MyReviews;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MyReviewsRepository extends CrudRepository<MyReviews, Long> {

    @Query("select * from public.my_reviews where user_id=:userId")
    List<MyReviews> findAllByUserId(@Param("userId") Long userId);

}
