package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.UserPreferredAmbience;

import java.util.List;

public interface IUserPreferredAmbienceService {

    List<UserPreferredAmbience> findUserPreferredAmbienceByUserId(Long userId);

    UserPreferredAmbience save(UserPreferredAmbience userPreferredAmbience);

}
