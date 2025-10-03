package com.project.dine.right.services;

import com.project.dine.right.interfaces.IOnboardingService;
import com.project.dine.right.jdbc.interfaces.IUserDataService;
import com.project.dine.right.jdbc.models.UserData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

@Service
public class OnboardingService implements IOnboardingService {

    @Value("${dine.right.secret}")
    private static String secret;

    @Autowired
    IUserDataService userDataService;

    @Override
    public UserData userLogin(String username, String password) {

        try {

            //Initializing AES-256 cipher and encrypting password
            var cipher = Cipher.getInstance("AES-256");
            cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(secret.getBytes(), "AES-256"));
            var encryptedString = Base64.getEncoder().encodeToString(cipher.doFinal(password.getBytes()));

            //Fetching user with encrypted password
            var userData = userDataService.getUserDataByEmailAndEncryptedPassword(username, encryptedString);

            return userData.orElse(null);

        } catch (Exception ignored) {
            return null;
        }
    }
}
