package com.project.dine.right.jdbc.services;

import com.project.dine.right.jdbc.interfaces.IUserDataService;
import com.project.dine.right.jdbc.models.UserData;
import com.project.dine.right.jdbc.repositories.UserDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserDataService implements IUserDataService {

    @Autowired
    UserDataRepository userDataRepository;

    @Override
    public Optional<UserData> getUserDataByEmailAndEncryptedPassword(String email, String encryptedPassword) {
        return Optional.ofNullable(userDataRepository.getUserDataByEmailAndEncryptedPassword(email, encryptedPassword));
    }
}
