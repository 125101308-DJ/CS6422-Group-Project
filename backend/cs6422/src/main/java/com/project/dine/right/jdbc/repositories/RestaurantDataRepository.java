package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.RestaurantData;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RestaurantDataRepository extends CrudRepository<RestaurantData, Long> {
}
