package com.project.dine.right.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.project.dine.right.dto.vo.WishlistRestaurantVO;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
@JsonInclude(JsonInclude.Include.NON_NULL)
public class DashboardGetUserVisitedResponseDTO {

    private String code;

    private List<WishlistRestaurantVO> restaurantsVisited;

}
