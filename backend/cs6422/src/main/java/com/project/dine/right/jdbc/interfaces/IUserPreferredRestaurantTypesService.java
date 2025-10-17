package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.UserPreferredRestaurantTypes;

import java.util.List;

public interface IUserPreferredRestaurantTypesService {

    List<UserPreferredRestaurantTypes> findUserPreferredRestaurantTypesByUserId(Long userId);

    void save(UserPreferredRestaurantTypes userPreferredRestaurantTypes);

}
