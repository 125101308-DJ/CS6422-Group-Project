package com.project.dine.right.jdbc.repositories;

import com.project.dine.right.jdbc.models.PreferredAtmosphere;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface PreferredAtmosphereRepository extends CrudRepository<PreferredAtmosphere, Long> {

    @Query("select * from public.preferred_atmosphere where user_id=:userId")
    List<PreferredAtmosphere> findPreferredAtmosphereByUserId(@Param("userId") Long userId);

}
