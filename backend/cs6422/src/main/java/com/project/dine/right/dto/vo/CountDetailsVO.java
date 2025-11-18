package com.project.dine.right.dto.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
public class CountDetailsVO {

    private String name;

    private Long countOfReviewsWritten;

    private Long countOfRestaurantsVisited;

    private Long countOfWishlist;

}
