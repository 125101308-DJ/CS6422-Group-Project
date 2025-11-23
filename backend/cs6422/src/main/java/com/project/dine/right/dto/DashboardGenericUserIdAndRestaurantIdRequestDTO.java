package com.project.dine.right.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
public class DashboardGenericUserIdAndRestaurantIdRequestDTO {

    private Long userId;

    private Long restaurantId;

}
