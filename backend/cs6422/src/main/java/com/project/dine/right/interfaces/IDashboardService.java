package com.project.dine.right.interfaces;

import com.project.dine.right.dto.vo.RestaurantDataVO;

import java.util.List;

public interface IDashboardService {

    List<RestaurantDataVO> getRestaurants();

}
