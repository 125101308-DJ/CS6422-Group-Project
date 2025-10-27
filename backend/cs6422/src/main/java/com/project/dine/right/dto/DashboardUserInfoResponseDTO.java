package com.project.dine.right.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.project.dine.right.dto.vo.MyUserVO;
import com.project.dine.right.dto.vo.TopKRestaurantVO;
import com.project.dine.right.dto.vo.WishlistRestaurantVO;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
@JsonInclude(JsonInclude.Include.NON_NULL)
public class DashboardUserInfoResponseDTO {

    private String code;

    private MyUserVO user;

    private List<WishlistRestaurantVO> wishlistRestaurants;

    private List<TopKRestaurantVO> topKRestaurants;
}
