package com.project.dine.right.utils;

import com.project.dine.right.jdbc.interfaces.IUserDataService;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class UserDataUtils {

    @Getter
    private static final UserDataUtils instance = new UserDataUtils();

    @Autowired
    private IUserDataService userDataService;

    public boolean checkIfUserExists(Long userId) {
        return userDataService.getUserDataById(userId).isPresent();
    }

    public boolean checkIfUserExists(String username) {
        return userDataService.getUserDataByEmail(username).isPresent();
    }

}
