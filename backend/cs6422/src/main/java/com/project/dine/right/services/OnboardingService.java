package com.project.dine.right.services;

import com.project.dine.right.interfaces.IOnboardingService;
import com.project.dine.right.jdbc.interfaces.IUserDataService;
import com.project.dine.right.jdbc.models.UserData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.spec.SecretKeySpec;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

@Service
public class OnboardingService implements IOnboardingService {

    @Value("${dine.right.secret}")
    private static String secret;

    @Autowired
    IUserDataService userDataService;

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
}
