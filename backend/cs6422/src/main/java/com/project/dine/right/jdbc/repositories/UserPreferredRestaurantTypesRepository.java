package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.UserPreferredRestaurantTypes;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserPreferredRestaurantTypesRepository extends CrudRepository<UserPreferredRestaurantTypes, Long> {

    @Query("select * from public.user_preferred_restauranttype where user_id=:userId")
    List<UserPreferredRestaurantTypes> findUserPreferredRestaurantTypesByUserId(@Param("userId") Long userId);
}
