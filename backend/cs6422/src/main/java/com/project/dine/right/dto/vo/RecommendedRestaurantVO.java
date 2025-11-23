package com.project.dine.right.dto.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
public class RecommendedRestaurantVO {

    private Long placeId;

    private String name;

    private String location;

    private String cuisine;

}
