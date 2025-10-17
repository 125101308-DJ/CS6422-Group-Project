package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.UserPreferredAmenities;

import java.util.List;

public interface IUserPreferredAmenitiesService {

    List<UserPreferredAmenities> findUserPreferredAmenitiesByUserId(Long userId);

    void save(UserPreferredAmenities userPreferredAmbience);

}
