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
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.spec.SecretKeySpec;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.List;

@Service
public class OnboardingService implements IOnboardingService {

    @Value("${dine.right.secret}")
    private static String secret;

    @Autowired
    IUserDataService userDataService;

    @Autowired
    IUserPreferencesService userPreferencesService;

    @Autowired
    IUserPreferredCuisinesService userPreferredCuisinesService;

    @Autowired
    IUserPreferredAmbienceService userPreferredAmbienceService;

    private static String getEncryptedString(String password) throws NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException, IllegalBlockSizeException, BadPaddingException {
        //Initializing AES-256 cipher and encrypting password
        var cipher = Cipher.getInstance("AES-256");
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(secret.getBytes(), "AES-256"));
        return Base64.getEncoder().encodeToString(cipher.doFinal(password.getBytes()));
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
            userData.setUserName(name);

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
