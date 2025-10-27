package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IRestaurantDataService;
import com.project.dine.right.jdbc.models.RestaurantData;
import com.project.dine.right.jdbc.repositories.RestaurantDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.StreamSupport;

@Service
public class RestaurantDataService implements IRestaurantDataService {

    @Autowired
    private RestaurantDataRepository restaurantDataRepository;

    @Override
    public List<RestaurantData> findAll() {
        return StreamSupport.stream(restaurantDataRepository.findAll().spliterator(), false).toList();
    }

    @Override
    public RestaurantData findByRestaurantId(Long restaurantId) {
        return restaurantDataRepository.findById(restaurantId).orElse(null);
    }
}
