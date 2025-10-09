package com.project.dine.right.interfaces;

import com.project.dine.right.dto.vo.AmbienceVO;
import com.project.dine.right.dto.vo.CuisinesVO;
import com.project.dine.right.jdbc.models.UserData;

import java.util.List;

public interface IOnboardingService {

    UserData userLogin(String username, String password);

    boolean checkIfUserExists(String username);

    boolean checkIfUserExists(Long userId);

    UserData saveUser(String name, String username, String password);

    void saveAmbienceData(List<AmbienceVO> ambienceList, Long userId);

    void saveCuisinesData(List<CuisinesVO> cuisinesList, Long userId);

    void saveOtherPreferences(String priceRange, String location, String service, Long userId);

}
