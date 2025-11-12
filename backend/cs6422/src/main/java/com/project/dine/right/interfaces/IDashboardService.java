package com.project.dine.right.interfaces;

import com.project.dine.right.dto.vo.MyUserVO;
import com.project.dine.right.dto.vo.RestaurantsVO;
import com.project.dine.right.dto.vo.TopKRestaurantVO;
import com.project.dine.right.dto.vo.WishlistRestaurantVO;

import java.util.List;

public interface IDashboardService {

    List<RestaurantsVO> getRestaurants();

    RestaurantsVO getRestaurantById(Long id);

    MyUserVO getMyUser(Long userId);

    List<WishlistRestaurantVO> getWishlistRestaurants(Long userId);

    List<TopKRestaurantVO> getTopKRestaurants(Long userId);

}
