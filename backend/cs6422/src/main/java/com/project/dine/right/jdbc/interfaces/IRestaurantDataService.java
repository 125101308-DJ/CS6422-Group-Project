package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.RestaurantMetaData;

import java.util.List;

public interface IRestaurantDataService {

    List<RestaurantMetaData> findAll();

    RestaurantMetaData findByRestaurantId(Long restaurantId);
}
