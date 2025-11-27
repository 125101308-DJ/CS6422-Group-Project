package com.project.dine.right.services;

import com.project.dine.right.dto.vo.RestaurantsVO;
import com.project.dine.right.jdbc.interfaces.*;
import com.project.dine.right.jdbc.models.RestaurantMetaData;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
public class DashboardServiceTest {

    private DashboardService dashboardService;
    private IRestaurantDataService restaurantDataService;
    private IUserReviewsService userReviewsService;
    private IMyReviewsService myReviewsService;
    private IUserDataService userDataService;
    private IMyWishlistService myWishlistService;
    private ITopRestaurantsService topRestaurantsService;
    private IUserPreferencesService userPreferencesService;
    private IUserPreferredAmenitiesService userPreferredAmenitiesService;
    private IPreferredAtmosphereService preferredAtmosphereService;
    private IUserPreferredCuisinesService userPreferredCuisinesService;
    private IUserPreferredRestaurantTypesService userPreferredRestaurantTypesService;
  
    @BeforeEach
    void setup() {
        dashboardService = new DashboardService();

        restaurantDataService = Mockito.mock(IRestaurantDataService.class);
        userReviewsService = Mockito.mock(IUserReviewsService.class);
        myReviewsService = Mockito.mock(IMyReviewsService.class);
        userDataService = Mockito.mock(IUserDataService.class);
        myWishlistService = Mockito.mock(IMyWishlistService.class);
        topRestaurantsService = Mockito.mock(ITopRestaurantsService.class);
        userPreferencesService = Mockito.mock(IUserPreferencesService.class);
        userPreferredAmenitiesService = Mockito.mock(IUserPreferredAmenitiesService.class);
        preferredAtmosphereService = Mockito.mock(IPreferredAtmosphereService.class);
        userPreferredCuisinesService = Mockito.mock(IUserPreferredCuisinesService.class);
        userPreferredRestaurantTypesService = Mockito.mock(IUserPreferredRestaurantTypesService.class);

        // inject mocks
        dashboardService.aiModelSubProcessUtils = aiModelSubProcessUtils;
        dashboardService.restaurantDataService = restaurantDataService;
        dashboardService.userReviewsService = userReviewsService;
        dashboardService.myReviewsService = myReviewsService;
        dashboardService.userDataService = userDataService;
        dashboardService.myWishlistService = myWishlistService;
        dashboardService.topRestaurantsService = topRestaurantsService;
        dashboardService.userPreferencesService = userPreferencesService;
        dashboardService.userPreferredAmenitiesService = userPreferredAmenitiesService;
        dashboardService.preferredAtmosphereService = preferredAtmosphereService;
        dashboardService.userPreferredCuisinesService = userPreferredCuisinesService;
        dashboardService.userPreferredRestaurantTypesService = userPreferredRestaurantTypesService;
    }

    @Test
    void testGetRestaurants() {
        RestaurantMetaData r = new RestaurantMetaData();
        r.setName("Test Restaurant");
        r.setPlaceId(1L);

        Mockito.when(restaurantDataService.findAll()).thenReturn(List.of(r));

        List<RestaurantsVO> result = dashboardService.getRestaurants();
        assertEquals(1, result.size());
        assertEquals("Test Restaurant", result.get(0).getName());
    }
}
