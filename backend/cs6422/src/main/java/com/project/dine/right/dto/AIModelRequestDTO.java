package com.project.dine.right.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
public class AIModelRequestDTO {

    private String address;

    @JsonProperty("radius_km")
    private Long radiusKm;

    @JsonProperty("cuisine_type")
    private List<String> cuisineType;

    @JsonProperty("budget_filter")
    private Long budgetFilter;

    @JsonProperty("atmosphere_filter")
    private List<String> atmosphereFilter;

    @JsonProperty("amenities_filter")
    private List<String> amenitiesFilter;

    @JsonProperty("restaurant_type_filter")
    private List<String> restaurantTypeFilter;

    private Long n;

}
