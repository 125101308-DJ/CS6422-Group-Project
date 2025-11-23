package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IPreferredAtmosphereService;
import com.project.dine.right.jdbc.models.PreferredAtmosphere;
import com.project.dine.right.jdbc.repositories.PreferredAtmosphereRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PreferredAtmosphereService implements IPreferredAtmosphereService {

    @Autowired
    PreferredAtmosphereRepository preferredAtmosphereRepository;

    @Override
    public void save(PreferredAtmosphere preferredAtmosphere) {
        preferredAtmosphereRepository.save(preferredAtmosphere);
    }

    @Override
    public List<PreferredAtmosphere> findPreferredAtmosphereByUserId(Long userId) {
        return preferredAtmosphereRepository.findPreferredAtmosphereByUserId(userId);
    }
}
