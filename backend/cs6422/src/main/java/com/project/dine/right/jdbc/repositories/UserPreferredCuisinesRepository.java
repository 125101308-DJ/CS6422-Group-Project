package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.UserPreferredCuisines;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserPreferredCuisinesRepository extends CrudRepository<UserPreferredCuisines, Long> {

    @Query("select * from user_preferred_cuisines where user_id=:userId")
    List<UserPreferredCuisines> findUserPreferredCuisinesByUserId(@Param("userId") Long userId);
}
