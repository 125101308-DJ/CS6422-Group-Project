package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.UserPreferences;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserPreferencesRepository extends CrudRepository<UserPreferences, Long> {

    @Query("select * from public.user_preferences where user_id=:userId")
    List<UserPreferences> findUserPreferencesByUserId(@Param("userId") Long userId);
}
