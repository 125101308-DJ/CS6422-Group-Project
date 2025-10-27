package com.project.dine.right.dto.vo;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TopKRestaurantVO {

    private Long restaurantId;

    private String restaurantName;

    private Short rankingPosition;

}
