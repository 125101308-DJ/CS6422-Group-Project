package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IUserPreferredAmbienceService;
import com.project.dine.right.jdbc.models.UserPreferredAmbience;
import com.project.dine.right.jdbc.repositories.UserPreferredAmbienceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserPreferredAmbienceService implements IUserPreferredAmbienceService {

    @Autowired
    UserPreferredAmbienceRepository userPreferredAmbienceRepository;

    @Override
    public List<UserPreferredAmbience> findUserPreferredAmbienceByUserId(Long userId) {
        return userPreferredAmbienceRepository.findUserPreferredAmbienceByUserId(userId);
    }

    @Override
    public UserPreferredAmbience save(UserPreferredAmbience userPreferredAmbience) {
        return userPreferredAmbienceRepository.save(userPreferredAmbience);
    }
}
