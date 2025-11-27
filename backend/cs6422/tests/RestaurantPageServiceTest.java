package com.project.dine.right.services;

import com.project.dine.right.dto.RestaurantPageAddReviewRequestDTO;
import com.project.dine.right.jdbc.interfaces.IMyReviewsService;
import com.project.dine.right.jdbc.interfaces.IRestaurantDataService;
import com.project.dine.right.jdbc.interfaces.IUserDataService;
import com.project.dine.right.jdbc.interfaces.IUserReviewsService;
import com.project.dine.right.jdbc.models.RestaurantMetaData;
import com.project.dine.right.jdbc.models.UserData;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.Optional;

import static org.mockito.Mockito.times;

public class RestaurantPageServiceTest {

    private RestaurantPageService service;

    private IMyReviewsService myReviewsService;
    private IRestaurantDataService restaurantDataService;
    private IUserDataService userDataService;
    private IUserReviewsService userReviewsService;

    @BeforeEach
    void setup() {
        service = new RestaurantPageService();

        myReviewsService = Mockito.mock(IMyReviewsService.class);
        restaurantDataService = Mockito.mock(IRestaurantDataService.class);
        userDataService = Mockito.mock(IUserDataService.class);
        userReviewsService = Mockito.mock(IUserReviewsService.class);

        service.myReviewsService = myReviewsService;
        service.restaurantDataService = restaurantDataService;
        service.userDataService = userDataService;
        service.userReviewsService = userReviewsService;
    }

    @Test
    void testSaveReview() {
        RestaurantPageAddReviewRequestDTO req = new RestaurantPageAddReviewRequestDTO();
        req.setUserId(5L);
        req.setRestaurantId(10L);
        req.setComment("Good!");
        req.setUserRating(4L);

        RestaurantMetaData r = new RestaurantMetaData();
        r.setName("Test Restaurant");

        UserData user = new UserData();
        user.setName("Deepak");

        Mockito.when(restaurantDataService.findByRestaurantId(10L)).thenReturn(r);
        Mockito.when(userDataService.getUserDataById(5L)).thenReturn(Optional.of(user));

        service.saveReview(req);

        Mockito.verify(userReviewsService, times(1)).save(Mockito.any());
        Mockito.verify(myReviewsService, times(1)).save(Mockito.any());
    }
}
