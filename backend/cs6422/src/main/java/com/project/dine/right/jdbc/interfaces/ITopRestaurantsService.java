package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.TopRestaurants;

import java.util.List;

public interface ITopRestaurantsService {

    List<TopRestaurants> findByUserId(Long userId);

}
