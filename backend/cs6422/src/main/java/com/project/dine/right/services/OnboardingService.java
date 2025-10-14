package com.project.dine.right.services;

import com.project.dine.right.dto.vo.AmbienceVO;
import com.project.dine.right.dto.vo.CuisinesVO;
import com.project.dine.right.interfaces.IOnboardingService;
import com.project.dine.right.jdbc.interfaces.IUserDataService;
import com.project.dine.right.jdbc.interfaces.IUserPreferencesService;
import com.project.dine.right.jdbc.interfaces.IUserPreferredAmbienceService;
import com.project.dine.right.jdbc.interfaces.IUserPreferredCuisinesService;
import com.project.dine.right.jdbc.models.UserData;
import com.project.dine.right.jdbc.models.UserPreferences;
import com.project.dine.right.jdbc.models.UserPreferredAmbience;
import com.project.dine.right.jdbc.models.UserPreferredCuisines;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
import java.util.List;

@Service
public class OnboardingService implements IOnboardingService {

    private static String secret;
    private static String iv;
    @Autowired
    IUserDataService userDataService;
    @Autowired
    IUserPreferencesService userPreferencesService;
    @Autowired
    IUserPreferredCuisinesService userPreferredCuisinesService;
    @Autowired
    IUserPreferredAmbienceService userPreferredAmbienceService;
    @Value("${dine.right.secret}")
    private String keyString;
    @Value("${dine.right.iv}")
    private String ivKey;

    private static String getEncryptedString(String password) throws Exception {
        //Initializing AES-256 cipher and encrypting password
        var cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(secret.getBytes(), "AES"), new IvParameterSpec(iv.getBytes()));
        return Base64.getEncoder().encodeToString(cipher.doFinal(password.getBytes()));
    }

    @PostConstruct
    public void init() {
        secret = keyString;
        iv = ivKey;
    }

    @Override
    public UserData userLogin(String username, String password) {

        try {

            var encryptedString = getEncryptedString(password);

            //Fetching user with encrypted password
            var userData = userDataService.getUserDataByEmailAndEncryptedPassword(username, encryptedString);

            return userData.orElse(null);

        } catch (Exception ignored) {
            return null;
        }
    }

    @Override
    public boolean checkIfUserExists(String username) {
        return userDataService.getUserDataByEmail(username).isPresent();
    }

    @Override
    public boolean checkIfUserExists(Long userId) {
        return userDataService.getUserDataById(userId).isPresent();
    }

    @Override
    public UserData saveUser(String name, String username, String password) {
        try {

            var userData = new UserData();

            var encryptedString = getEncryptedString(password);

            userData.setEmail(username);
            userData.setPassword(encryptedString);
            userData.setName(name);

            return userDataService.save(userData).orElse(null);

        } catch (Exception ignored) {
            return null;
        }

    }

    @Override
    public void saveAmbienceData(List<AmbienceVO> ambienceList, Long userId) {
        try {
            var userPreferredAmbience = new UserPreferredAmbience();
            for (AmbienceVO ambience : ambienceList) {
                userPreferredAmbience.setUserId(userId);
                userPreferredAmbience.setPreferredAmbience(ambience.getName());
                userPreferredAmbienceService.save(userPreferredAmbience);
            }
        } catch (Exception ignored) {

        }
    }

    @Override
    public void saveCuisinesData(List<CuisinesVO> cuisinesList, Long userId) {
        try {
            var userPreferredCuisines = new UserPreferredCuisines();
            for (CuisinesVO cuisines : cuisinesList) {
                userPreferredCuisines.setUserId(userId);
                userPreferredCuisines.setPreferredCuisines(cuisines.getName());
                userPreferredCuisinesService.save(userPreferredCuisines);
            }
        } catch (Exception ignored) {

        }
    }

    @Override
    public void saveOtherPreferences(String priceRange, String location, String service, Long userId) {
        try {
            if (!StringUtils.hasLength(priceRange) && !StringUtils.hasLength(location) && !StringUtils.hasLength(service)) {
                return;
            }
            var userPreferences = new UserPreferences();
            userPreferences.setUserId(userId);
            userPreferences.setPreferredPriceRange(priceRange);
            userPreferences.setPreferredLocation(location);
            userPreferences.setPreferredService(service);
            userPreferencesService.save(userPreferences);
        } catch (Exception ignored) {

        }
    }
}
