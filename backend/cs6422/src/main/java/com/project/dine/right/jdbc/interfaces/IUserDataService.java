package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.UserData;

import java.util.Optional;

public interface IUserDataService {

    Optional<UserData> getUserDataByEmailAndEncryptedPassword(String email, String encryptedPassword);

}
