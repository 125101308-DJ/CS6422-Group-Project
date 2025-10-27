package com.project.dine.right.interfaces;

import com.project.dine.right.dto.vo.MyUserVO;
import com.project.dine.right.dto.vo.RestaurantDataVO;
import com.project.dine.right.dto.vo.TopKRestaurantVO;
import com.project.dine.right.dto.vo.WishlistRestaurantVO;

import java.util.List;

public interface IDashboardService {

    List<RestaurantDataVO> getRestaurants();

    MyUserVO getMyUser(Long userId);

    List<WishlistRestaurantVO> getWishlistRestaurants(Long userId);

    List<TopKRestaurantVO> getTopKRestaurants(Long userId);

}
