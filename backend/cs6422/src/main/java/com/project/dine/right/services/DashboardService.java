package com.project.dine.right.services;

import com.project.dine.right.dto.vo.RestaurantDataVO;
import com.project.dine.right.dto.vo.ReviewsVO;
import com.project.dine.right.interfaces.IDashboardService;
import com.project.dine.right.jdbc.interfaces.IRestaurantDataService;
import com.project.dine.right.jdbc.interfaces.IUserReviewsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class DashboardService implements IDashboardService {

    @Autowired
    IRestaurantDataService restaurantDataService;

    @Autowired
    IUserReviewsService userReviewsService;

    @Override
    public List<RestaurantDataVO> getRestaurants() {

        var resultLst = new ArrayList<RestaurantDataVO>();
        var restaurants = restaurantDataService.findAll();

        for (var restaurant : restaurants) {
            var restaurantDataVO = new RestaurantDataVO();
            restaurantDataVO.setName(restaurant.getName());
            restaurantDataVO.setId(restaurant.getPlaceId());
            restaurantDataVO.setLocation(restaurant.getAddress());
            restaurantDataVO.setCuisine(restaurant.getCuisineType());

            var restaurantReviews = userReviewsService.findAllByPlaceId(restaurant.getPlaceId());

            // With Java streams, create the List of Reviews for our Response Object from the result of the query with one line
            restaurantDataVO.setReviews(restaurantReviews.stream()
                    .map(o -> {
                        var n = new ReviewsVO();
                        n.setUser(o.getUsername());
                        n.setRating(o.getRating());
                        n.setComment(o.getReviewText());
                        return n;
                    }).toList());

            resultLst.add(restaurantDataVO);
        }

        return resultLst;
    }
}
