package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IUserPreferredCuisinesService;
import com.project.dine.right.jdbc.models.UserPreferredCuisines;
import com.project.dine.right.jdbc.repositories.UserPreferredCuisinesRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserPreferredCuisinesService implements IUserPreferredCuisinesService {

    @Autowired
    private UserPreferredCuisinesRepository userPreferredCuisinesRepository;

    @Override
    public List<UserPreferredCuisines> findUserPreferredCuisinesByUserId(Long userId) {
        return userPreferredCuisinesRepository.findUserPreferredCuisinesByUserId(userId);
    }

    @Override
    public UserPreferredCuisines save(UserPreferredCuisines userPreferredCuisines) {
        return userPreferredCuisinesRepository.save(userPreferredCuisines);
    }
}
