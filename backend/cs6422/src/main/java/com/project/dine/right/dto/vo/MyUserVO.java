package com.project.dine.right.dto.vo;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
@JsonInclude(JsonInclude.Include.NON_NULL)
public class MyUserVO {

    private Long userId;

    private String username;

    private MyUserTotalReviewsVO totalReviews;
}
