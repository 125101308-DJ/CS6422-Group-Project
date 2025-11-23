package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.UserPreferences;

public interface IUserPreferencesService {

    UserPreferences findUserPreferencesByUserId(Long userId);

    void save(UserPreferences userPreferences);

}
