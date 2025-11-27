package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.RestaurantsVisited;

import java.util.List;

public interface IRestaurantsVisitedService {

    List<RestaurantsVisited> findByUserId(Long userId);

    Long countMyVisited();

    RestaurantsVisited save(RestaurantsVisited restaurantsVisited);

    void deleteByUserIdAndPlaceId(Long userId, Long restaurantId);
}
