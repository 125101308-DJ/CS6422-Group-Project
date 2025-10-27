package com.project.dine.right.interfaces;

import com.project.dine.right.dto.vo.AmenitiesVO;
import com.project.dine.right.dto.vo.CuisinesVO;
import com.project.dine.right.dto.vo.RestaurantTypesVO;
import com.project.dine.right.jdbc.models.UserData;

import java.util.List;

public interface IOnboardingService {

    UserData userLogin(String username, String password);

    UserData saveUser(String name, String username, String password);

    void saveAmenitiesData(List<AmenitiesVO> amenitiesVOList, Long userId);

    void saveCuisinesData(List<CuisinesVO> cuisinesList, Long userId);

    void saveOtherPreferences(String priceRange, String location, String service, Long userId);

    void saveRestaurantTypesData(List<RestaurantTypesVO> restaurantTypesVOS, Long userId);
}
