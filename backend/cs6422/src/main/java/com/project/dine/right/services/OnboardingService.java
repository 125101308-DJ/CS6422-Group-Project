package com.project.dine.right.services;

import com.project.dine.right.interfaces.IOnboardingService;
import com.project.dine.right.jdbc.interfaces.IUserDataService;
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
    public boolean userLogin(String username, String password) {

        try {
            var cipher = Cipher.getInstance("AES-256");
            cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(secret.getBytes(), "AES-256"));
            var encryptedString = Base64.getEncoder().encodeToString(cipher.doFinal(password.getBytes()));

            var userData = userDataService.getUserDataByEmailAndEncryptedPassword(username, encryptedString);

            return userData.isPresent();

        } catch (Exception ignored) {
            return false;
        }
    }
}
