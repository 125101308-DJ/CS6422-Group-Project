package com.project.dine.right.dto.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
public class PreferenceObjectVO {

    private Long priceLevel;

    private String location;

    private String atmosphere;

    private String radius;

    private List<AmenitiesVO> amenities;

    private List<CuisinesVO> cuisines;

    private List<RestaurantTypesVO> restaurantTypes;

}
