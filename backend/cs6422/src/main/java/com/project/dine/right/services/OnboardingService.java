package com.project.dine.right.services;

import com.project.dine.right.dto.vo.AmenitiesVO;
import com.project.dine.right.dto.vo.CuisinesVO;
import com.project.dine.right.dto.vo.RestaurantTypesVO;
import com.project.dine.right.interfaces.IOnboardingService;
import com.project.dine.right.jdbc.interfaces.*;
import com.project.dine.right.jdbc.models.*;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.ObjectUtils;
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
    IUserPreferredAmenitiesService userPreferredAmenitiesService;
    @Autowired
    IUserPreferredRestaurantTypesService userPreferredRestaurantTypesService;
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
    public void saveAmenitiesData(List<AmenitiesVO> amenitiesVOList, Long userId) {
        try {
            for (AmenitiesVO ambience : amenitiesVOList) {
                var userPreferredAmenities = new UserPreferredAmenities();
                userPreferredAmenities.setUserId(userId);
                userPreferredAmenities.setPreferredAmenities(ambience.getName());
                userPreferredAmenitiesService.save(userPreferredAmenities);
            }
        } catch (Exception ignored) {

        }
    }

    @Override
    public void saveCuisinesData(List<CuisinesVO> cuisinesList, Long userId) {
        try {
            for (CuisinesVO cuisines : cuisinesList) {
                var userPreferredCuisines = new UserPreferredCuisines();
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
            if (ObjectUtils.isEmpty(priceRange) && !StringUtils.hasLength(location) && !StringUtils.hasLength(service)) {
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

    @Override
    public void saveRestaurantTypesData(List<RestaurantTypesVO> restaurantTypesVOS, Long userId) {
        try {
            for (RestaurantTypesVO restaurantTypes : restaurantTypesVOS) {
                var userPreferredRestaurantTypes = new UserPreferredRestaurantTypes();
                userPreferredRestaurantTypes.setUserId(userId);
                userPreferredRestaurantTypes.setPreferredRestaurantType(restaurantTypes.getName());
                userPreferredRestaurantTypesService.save(userPreferredRestaurantTypes);
            }
        } catch (Exception ignored) {

        }
    }
}
