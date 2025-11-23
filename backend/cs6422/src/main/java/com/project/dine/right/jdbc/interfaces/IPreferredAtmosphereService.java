package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.PreferredAtmosphere;

import java.util.List;

public interface IPreferredAtmosphereService {

    void save(PreferredAtmosphere preferredAtmosphere);

    List<PreferredAtmosphere> findPreferredAtmosphereByUserId(Long userId);
}
