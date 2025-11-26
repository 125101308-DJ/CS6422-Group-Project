package com.project.dine.right.services;

import com.project.dine.right.dto.AIModelRequestDTO;
import com.project.dine.right.dto.vo.*;
import com.project.dine.right.interfaces.IDashboardService;
import com.project.dine.right.jdbc.interfaces.*;
import com.project.dine.right.jdbc.models.MyWishlist;
import com.project.dine.right.jdbc.models.RestaurantMetaData;
import com.project.dine.right.utils.AIModelSubProcessUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.ObjectUtils;

import java.util.ArrayList;
import java.util.List;

@Service
public class DashboardService implements IDashboardService {

    @Autowired
    private AIModelSubProcessUtils aiModelSubProcessUtils;

    @Autowired
    private IRestaurantDataService restaurantDataService;

    @Autowired
    private IUserReviewsService userReviewsService;

    @Autowired
    private IMyReviewsService myReviewsService;

    @Autowired
    private IUserDataService userDataService;

    @Autowired
    private IMyWishlistService myWishlistService;

    @Autowired
    private ITopRestaurantsService topRestaurantsService;

    @Autowired
    private IUserPreferencesService userPreferencesService;

    @Autowired
    private IUserPreferredAmenitiesService userPreferredAmenitiesService;

    @Autowired
    private IPreferredAtmosphereService preferredAtmosphereService;

    @Autowired
    private IUserPreferredCuisinesService userPreferredCuisinesService;

    @Autowired
    private IUserPreferredRestaurantTypesService userPreferredRestaurantTypesService;

    @Override
    public List<RestaurantsVO> getRestaurants() {

        var resultLst = new ArrayList<RestaurantsVO>();
        var restaurants = restaurantDataService.findAll();

        for (var restaurant : restaurants) {
            var restaurantsVO = getRestaurantsVO(restaurant);

            resultLst.add(restaurantsVO);
        }

        return resultLst;
    }

    @Override
    public RestaurantsVO getRestaurantById(Long id) {

        var restaurant = restaurantDataService.findByRestaurantId(id);

        if (!ObjectUtils.isEmpty(restaurant)) {

            return getRestaurantsVO(restaurant);

        }

        return null;
    }

    @Override
    public MyUserVO getMyUser(Long userId) {
        var userVO = new MyUserVO();

        var user = userDataService.getUserDataById(userId);

        user.ifPresent(u -> {
            userVO.setUserId(userId);
            userVO.setUsername(user.get().getName());

            var myUserReviews = myReviewsService.findAllByUserId(userId);

            var totalReviewsVO = new MyUserTotalReviewsVO();

            // With Java streams, create the List of Reviews for our Response Object from the result of the query with one line
            if (!myUserReviews.isEmpty()) {
                totalReviewsVO.setCount(myUserReviews.size());
                totalReviewsVO.setReviews(myUserReviews.stream()
                        .map(o -> {
                            var n = new MyUserReviewVO();
                            n.setReviewId(String.valueOf(o.getId()));
                            n.setComment(o.getReviewText());
                            n.setRestaurantId(String.valueOf(o.getPlaceId()));
                            var restaurant = restaurantDataService.findByRestaurantId(o.getPlaceId());
                            n.setRestaurantName(restaurant.getName());
                            n.setComment(o.getReviewText());
                            n.setRating(Integer.valueOf(o.getRating()));
                            return n;
                        }).toList());
            } else {
                totalReviewsVO.setCount(0);
            }

            userVO.setTotalReviews(totalReviewsVO);
        });

        return userVO;
    }

    @Override
    public CountDetailsVO getCountDetails(Long userId) {

        var countDetailsVO = new CountDetailsVO();

        var user = userDataService.getUserDataById(userId);

        countDetailsVO.setName(user.get().getName());
        countDetailsVO.setCountOfWishlist(myWishlistService.countMyWishlists());
        countDetailsVO.setCountOfReviewsWritten(myReviewsService.countMyReviews());

        return countDetailsVO;
    }

    @Override
    public List<WishlistRestaurantVO> getWishlistRestaurants(Long userId) {
        var resultLst = new ArrayList<WishlistRestaurantVO>();

        var myWishlist = myWishlistService.findByUserId(userId);

        for (var wishlistRestaurant : myWishlist) {
            var wishlistRestaurantVO = new WishlistRestaurantVO();

            wishlistRestaurantVO.setRestaurantId(wishlistRestaurant.getId());
            var restaurant = restaurantDataService.findByRestaurantId(wishlistRestaurant.getPlaceId());
            wishlistRestaurantVO.setRestaurantName(restaurant.getName());
            wishlistRestaurantVO.setLocation(restaurant.getAddress());
            wishlistRestaurantVO.setCuisine(restaurant.getCuisineType());
            wishlistRestaurantVO.setRating(String.valueOf(restaurant.getRating()));

            resultLst.add(wishlistRestaurantVO);
        }

        return resultLst;
    }

    @Override
    public List<TopKRestaurantVO> getTopKRestaurants(Long userId) {
        var resultLst = new ArrayList<TopKRestaurantVO>();

        var topRestaurants = topRestaurantsService.findByUserId(userId);

        for (var topRestaurant : topRestaurants) {
            var topKRestaurant = new TopKRestaurantVO();

            topKRestaurant.setRestaurantId(topRestaurant.getId());
            var restaurant = restaurantDataService.findByRestaurantId(topRestaurant.getPlaceId());
            topKRestaurant.setRestaurantName(restaurant.getName());
            topKRestaurant.setRankingPosition(topRestaurant.getRank().shortValue());

            resultLst.add(topKRestaurant);
        }

        return resultLst;
    }

    @Override
    public List<RecommendedRestaurantVO> getRecommendedRestaurants(Long userId) {

        var resultLst = new ArrayList<RecommendedRestaurantVO>();
        var modelRequest = new AIModelRequestDTO();

        var userPreferences = userPreferencesService.findUserPreferencesByUserId(userId);

        modelRequest.setRadiusKm(Long.valueOf(userPreferences.getRadius()));
        modelRequest.setAddress(userPreferences.getPreferredLocation());
        modelRequest.setBudgetFilter(userPreferences.getPreferredPriceRange());

        var userPreferredAmenities = userPreferredAmenitiesService.findUserPreferredAmenitiesByUserId(userId);

        if (userPreferredAmenities != null && !userPreferredAmenities.isEmpty()) {

            var amenities = new ArrayList<String>();
            for (var amenity : userPreferredAmenities) {
                amenities.add(amenity.getPreferredAmenities());
            }
            modelRequest.setAmenitiesFilter(amenities);

        }

        var userPreferredCuisines = userPreferredCuisinesService.findUserPreferredCuisinesByUserId(userId);

        if (userPreferredCuisines != null && !userPreferredCuisines.isEmpty()) {

            var cuisines = new ArrayList<String>();
            for (var cuisine : userPreferredCuisines) {
                cuisines.add(cuisine.getPreferredCuisines());
            }
            modelRequest.setCuisineType(cuisines);

        }

        var userRestaurantTypes = userPreferredRestaurantTypesService.findUserPreferredRestaurantTypesByUserId(userId);

        if (userRestaurantTypes != null && !userRestaurantTypes.isEmpty()) {

            var restaurantTypes = new ArrayList<String>();
            for (var restaurant : userRestaurantTypes) {
                restaurantTypes.add(restaurant.getPreferredRestaurantType());
            }
            modelRequest.setRestaurantTypeFilter(restaurantTypes);

        }

        var userPreferredAtmosphere = preferredAtmosphereService.findPreferredAtmosphereByUserId(userId);

        if (userPreferredAtmosphere != null && !userPreferredAtmosphere.isEmpty()) {

            var preferredAtmosphere = new ArrayList<String>();
            for (var atmosphere : userPreferredAtmosphere) {
                preferredAtmosphere.add(atmosphere.getPreferredAtmosphere());
            }
            modelRequest.setAtmosphereFilter(preferredAtmosphere);

        }

        var recommendationsIdList = aiModelSubProcessUtils.getRecommendations(modelRequest);

        for (var id : recommendationsIdList) {

            var recommendedRestaurant = new RecommendedRestaurantVO();
            var restaurant = restaurantDataService.findByRestaurantId(id);
            recommendedRestaurant.setPlaceId(id);
            recommendedRestaurant.setName(restaurant.getName());
            recommendedRestaurant.setLocation(restaurant.getAddress());
            recommendedRestaurant.setCuisine(restaurant.getCuisineType());
            resultLst.add(recommendedRestaurant);

        }

        return resultLst;
    }

    @Override
    public List<WishlistRestaurantVO> getUserWishlist(Long userId) {
        var myWishlist = myWishlistService.findByUserId(userId);

        var returnList = new ArrayList<WishlistRestaurantVO>();

        for (var wishlist : myWishlist) {
            var wishlistRestaurant = new WishlistRestaurantVO();
            wishlistRestaurant.setRestaurantId(wishlist.getPlaceId());
            wishlistRestaurant.setRestaurantName(restaurantDataService.findByRestaurantId(wishlist.getPlaceId()).getName());
            returnList.add(wishlistRestaurant);
        }

        return returnList;
    }

    @Override
    public List<MyUserReviewVO> getUserReviewsWritten(Long userId) {

        var userReviews = myReviewsService.findAllByUserId(userId);

        var returnList = new ArrayList<MyUserReviewVO>();

        for (var userReview : userReviews) {
            var myUserReviewVO = new MyUserReviewVO();
            myUserReviewVO.setRestaurantId(String.valueOf(userReview.getPlaceId()));
            myUserReviewVO.setRestaurantName(restaurantDataService.findByRestaurantId(userReview.getPlaceId()).getName());
            myUserReviewVO.setComment(userReview.getReviewText());
            returnList.add(myUserReviewVO);
        }

        return returnList;
    }

    @Override
    public void addToUserWishlist(Long userId, Long restaurantId) {

        var myWishlist = new MyWishlist();

        myWishlist.setUserId(userId);
        myWishlist.setPlaceId(restaurantId);

        myWishlistService.save(myWishlist);
    }

    @Override
    public void removeToUserWishlist(Long userId, Long restaurantId) {
        myWishlistService.deleteByUserIdAndPlaceId(userId, restaurantId);
    }

    private RestaurantsVO getRestaurantsVO(RestaurantMetaData restaurant) {
        var restaurantsVO = new RestaurantsVO();
        restaurantsVO.setName(restaurant.getName());
        restaurantsVO.setPlaceId(restaurant.getPlaceId());
        restaurantsVO.setAddress(restaurant.getAddress());
        restaurantsVO.setCuisine(restaurant.getCuisineType());
        restaurantsVO.setRestaurantType(restaurant.getRestaurantType());
        restaurantsVO.setPriceRange(restaurant.getPriceRange());
        restaurantsVO.setOverallRating(String.valueOf(restaurant.getRating()));
        restaurantsVO.setAmenities(restaurant.getAmenities());
        restaurantsVO.setAtmosphere(restaurant.getAtmosphere());
        restaurantsVO.setPhone(restaurant.getPhone());

        var restaurantReviews = userReviewsService.findAllByPlaceId(restaurant.getPlaceId());

        // With Java streams, create the List of Reviews for our Response Object from the result of the query with one line
        if (!restaurantReviews.isEmpty()) {
            restaurantsVO.setReviews(restaurantReviews.stream()
                    .map(o -> {
                        var n = new ReviewsVO();
                        n.setUser(o.getUsername());
                        n.setRating(o.getRating());
                        n.setComment(o.getReviewText());
                        return n;
                    }).toList());
        }
        return restaurantsVO;
    }
}
