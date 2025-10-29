package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.RestaurantMetaData;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RestaurantDataRepository extends CrudRepository<RestaurantMetaData, Long> {
}
