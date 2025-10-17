package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IUserPreferredAmenitiesService;
import com.project.dine.right.jdbc.models.UserPreferredAmenities;
import com.project.dine.right.jdbc.repositories.UserPreferredAmenitiesRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserPreferredAmenitiesService implements IUserPreferredAmenitiesService {

    @Autowired
    UserPreferredAmenitiesRepository userPreferredAmbienceRepository;

    @Override
    public List<UserPreferredAmenities> findUserPreferredAmenitiesByUserId(Long userId) {
        return userPreferredAmbienceRepository.findUserPreferredAmenitiesByUserId(userId);
    }

    @Override
    public void save(UserPreferredAmenities userPreferredAmenities) {
        userPreferredAmbienceRepository.save(userPreferredAmenities);
    }
}
