package com.project.dine.right.services;

import com.project.dine.right.dto.vo.*;
import com.project.dine.right.interfaces.IDashboardService;
import com.project.dine.right.jdbc.interfaces.*;
import com.project.dine.right.jdbc.models.RestaurantMetaData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.ObjectUtils;

import java.util.ArrayList;
import java.util.List;

@Service
public class DashboardService implements IDashboardService {

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
                            n.setDate(o.getReviewDate());
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
