package com.project.dine.right.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.project.dine.right.dto.vo.RecommendedRestaurantVO;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
@JsonInclude(JsonInclude.Include.NON_NULL)
public class DashboardRecommendationsResponseDTO {

    private String code;

    private List<RecommendedRestaurantVO> recommendedRestaurants;

}
