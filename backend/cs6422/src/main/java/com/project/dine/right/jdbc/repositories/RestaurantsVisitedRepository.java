package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.RestaurantsVisited;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RestaurantsVisitedRepository extends CrudRepository<RestaurantsVisited, Long> {

    @Query("select * from public.restaurants_visited where user_id=:userId")
    List<RestaurantsVisited> findByUserId(@Param("userId") Long userId);

    @Query("delete from public.restaurants_visited where user_id=:userId and place_id=:restaurantId")
    void deleteByUserIdAndPlaceId(@Param("userId") Long userId, @Param("restaurantId") Long restaurantId);

}
