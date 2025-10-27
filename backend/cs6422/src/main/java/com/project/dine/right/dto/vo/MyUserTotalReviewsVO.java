package com.project.dine.right.dto.vo;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@ToString
@JsonInclude(JsonInclude.Include.NON_NULL)
public class MyUserTotalReviewsVO {

    private Integer count;

    private List<MyUserReviewVO> reviews;

}
