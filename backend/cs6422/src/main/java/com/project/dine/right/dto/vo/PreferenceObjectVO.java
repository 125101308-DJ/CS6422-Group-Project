package com.project.dine.right.dto.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
public class PreferenceObjectVO {

    private String priceRange;

    private String location;

    private String service;

    private List<AmenitiesVO> amenities;

    private List<CuisinesVO> cuisines;

    private List<RestaurantTypesVO> restaurantTypes;

}
