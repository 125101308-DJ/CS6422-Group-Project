package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IUserPreferredRestaurantTypesService;
import com.project.dine.right.jdbc.models.UserPreferredRestaurantTypes;
import com.project.dine.right.jdbc.repositories.UserPreferredRestaurantTypesRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserPreferredRestaurantTypesService implements IUserPreferredRestaurantTypesService {

    @Autowired
    UserPreferredRestaurantTypesRepository userPreferredRestaurantTypesRepository;

    @Override
    public List<UserPreferredRestaurantTypes> findUserPreferredRestaurantTypesByUserId(Long userId) {
        return userPreferredRestaurantTypesRepository.findUserPreferredRestaurantTypesByUserId(userId);
    }

    @Override
    public void save(UserPreferredRestaurantTypes userPreferredRestaurantTypes) {
        userPreferredRestaurantTypesRepository.save(userPreferredRestaurantTypes);
    }
}
