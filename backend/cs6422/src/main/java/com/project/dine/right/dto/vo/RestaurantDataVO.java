package com.project.dine.right.dto.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
public class RestaurantDataVO {

    private Long id;

    private String name;

    private String location;

    private String cuisine;

    private List<ReviewsVO> reviews;

}
