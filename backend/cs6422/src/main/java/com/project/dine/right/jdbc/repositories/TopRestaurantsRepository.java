package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.TopRestaurants;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface TopRestaurantsRepository extends CrudRepository<TopRestaurants, Long> {

    @Query("select * from public.top_restaurants where user_id=:userId")
    List<TopRestaurants> findByUserId(@Param("userId") Long userId);

}
