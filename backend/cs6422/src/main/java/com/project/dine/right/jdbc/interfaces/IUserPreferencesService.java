package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.UserPreferences;

import java.util.List;

public interface IUserPreferencesService {

    List<UserPreferences> findUserPreferencesByUserId(Long userId);

    void save(UserPreferences userPreferences);

}
