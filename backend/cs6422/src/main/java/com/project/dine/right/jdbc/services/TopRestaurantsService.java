package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.ITopRestaurantsService;
import com.project.dine.right.jdbc.models.TopRestaurants;
import com.project.dine.right.jdbc.repositories.TopRestaurantsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TopRestaurantsService implements ITopRestaurantsService {

    @Autowired
    private TopRestaurantsRepository topRestaurantsRepository;

    @Override
    public List<TopRestaurants> findByUserId(Long userId) {
        return topRestaurantsRepository.findByUserId(userId);
    }
}
