package com.project.dine.right.services;

import com.project.dine.right.jdbc.interfaces.*;
import com.project.dine.right.jdbc.models.UserData;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

public class OnboardingServiceTest {

    private OnboardingService onboardingService;
    private IUserDataService userDataService;

    @BeforeEach
    void setup() {
        onboardingService = new OnboardingService();

        userDataService = Mockito.mock(IUserDataService.class);
        onboardingService.userDataService = userDataService;

        onboardingService.init(); 
    }

    @Test
    void testUserLogin_UserExists() {
        UserData mockUser = new UserData();
        mockUser.setUserId(10L);

        Mockito.when(userDataService.getUserDataByEmailAndEncryptedPassword(Mockito.anyString(), Mockito.anyString()))
                .thenReturn(Optional.of(mockUser));

        UserData result = onboardingService.userLogin("test@email.com", "password");
        assertNotNull(result);
        assertEquals(10L, result.getUserId());
    }

    @Test
    void testUserLogin_UserNotFound() {
        Mockito.when(userDataService.getUserDataByEmailAndEncryptedPassword(Mockito.anyString(), Mockito.anyString()))
                .thenReturn(Optional.empty());

        UserData result = onboardingService.userLogin("x@x.com", "wrong");
        assertNull(result);
    }
}
