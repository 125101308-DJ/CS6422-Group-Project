package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.RestaurantData;

import java.util.List;

public interface IRestaurantDataService {

    List<RestaurantData> findAll();

    RestaurantData findByRestaurantId(Long restaurantId);
}
