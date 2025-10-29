package com.project.dine.right.utils;

import com.project.dine.right.jdbc.interfaces.IUserDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class UserDataUtils {

    @Autowired
    private IUserDataService userDataService;

    public boolean checkIfUserExists(Long userId) {
        return userDataService.getUserDataById(userId).isPresent();
    }

    public boolean checkIfUserExists(String username) {
        return userDataService.getUserDataByEmail(username).isPresent();
    }

}
