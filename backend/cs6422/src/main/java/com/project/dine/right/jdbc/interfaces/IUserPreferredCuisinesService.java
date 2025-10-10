package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.UserPreferredCuisines;

import java.util.List;

public interface IUserPreferredCuisinesService {

    List<UserPreferredCuisines> findUserPreferredCuisinesByUserId(Long userId);

    UserPreferredCuisines save(UserPreferredCuisines userPreferredCuisines);

}
