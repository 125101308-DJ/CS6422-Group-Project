package com.project.dine.right.dto.vo;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class PreferenceObjectVO {

    private String priceRange;

    private String location;

    private String service;

    private List<AmbienceVO> ambience;

    private List<CuisinesVO> cuisines;

}
