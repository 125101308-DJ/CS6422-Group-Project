package com.project.dine.right.interfaces;

import com.project.dine.right.dto.vo.*;

import java.util.List;

public interface IDashboardService {

    List<RestaurantsVO> getRestaurants();

    RestaurantsVO getRestaurantById(Long id);

    MyUserVO getMyUser(Long userId);

    CountDetailsVO getCountDetails(Long userId);

    List<WishlistRestaurantVO> getWishlistRestaurants(Long userId);

    List<TopKRestaurantVO> getTopKRestaurants(Long userId);

}
