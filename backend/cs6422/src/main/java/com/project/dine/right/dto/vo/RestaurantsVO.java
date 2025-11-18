package com.project.dine.right.dto.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
public class RestaurantsVO {

    private Long placeId;

    private String name;

    private String restaurantType;

    private String priceRange;

    private String phone;

    private String atmosphere;

    private String amenities;

    private String address;

    private String cuisine;

    private String overallRating;

    private List<ReviewsVO> reviews;

}
