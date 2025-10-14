package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.UserPreferredAmbience;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserPreferredAmbienceRepository extends CrudRepository<UserPreferredAmbience, Long> {

    @Query("select * from public.user_preferred_ambience where user_id=:userId")
    List<UserPreferredAmbience> findUserPreferredAmbienceByUserId(@Param("userId") Long userId);
}
