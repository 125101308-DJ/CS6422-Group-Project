package com.project.dine.right.interfaces;

import com.project.dine.right.jdbc.models.UserData;

public interface IOnboardingService {

    UserData userLogin(String username, String password);

    boolean checkIfUserExists(String username);

    UserData saveUser(String name, String username, String password);

}
