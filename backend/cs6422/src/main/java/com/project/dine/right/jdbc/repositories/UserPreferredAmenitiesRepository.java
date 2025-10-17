package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.UserPreferredAmenities;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserPreferredAmenitiesRepository extends CrudRepository<UserPreferredAmenities, Long> {

    @Query("select * from public.user_preferred_amenities where user_id=:userId")
    List<UserPreferredAmenities> findUserPreferredAmenitiesByUserId(@Param("userId") Long userId);

}
