package com.project.dine.right.dto;


import com.fasterxml.jackson.annotation.JsonInclude;
import com.project.dine.right.dto.vo.CountDetailsVO;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
@JsonInclude(JsonInclude.Include.NON_NULL)
public class DashboardUserMetricsResponseDTO {

    private String code;

    private CountDetailsVO countDetails;

}
