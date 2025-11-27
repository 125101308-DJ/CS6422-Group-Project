package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IRestaurantsVisitedService;
import com.project.dine.right.jdbc.models.RestaurantsVisited;
import com.project.dine.right.jdbc.repositories.RestaurantsVisitedRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RestaurantsVisitedService implements IRestaurantsVisitedService {

    @Autowired
    private RestaurantsVisitedRepository restaurantsVisitedRepository;

    @Override
    public List<RestaurantsVisited> findByUserId(Long userId) {
        return restaurantsVisitedRepository.findByUserId(userId);
    }

    @Override
    public Long countMyVisited() {
        return restaurantsVisitedRepository.count();
    }

    @Override
    public RestaurantsVisited save(RestaurantsVisited restaurantsVisited) {
        return restaurantsVisitedRepository.save(restaurantsVisited);
    }

    @Override
    public void deleteByUserIdAndPlaceId(Long userId, Long restaurantId) {
        restaurantsVisitedRepository.deleteByUserIdAndPlaceId(userId, restaurantId);
    }
}
