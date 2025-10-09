package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IUserPreferencesService;
import com.project.dine.right.jdbc.models.UserPreferences;
import com.project.dine.right.jdbc.repositories.UserPreferencesRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserPreferencesService implements IUserPreferencesService {

    @Autowired
    UserPreferencesRepository userPreferencesRepository;

    @Override
    public List<UserPreferences> findUserPreferencesByUserId(Long userId) {
        return userPreferencesRepository.findUserPreferencesByUserId(userId);
    }

    @Override
    public UserPreferences save(UserPreferences userPreferences) {
        return userPreferencesRepository.save(userPreferences);
    }
}
