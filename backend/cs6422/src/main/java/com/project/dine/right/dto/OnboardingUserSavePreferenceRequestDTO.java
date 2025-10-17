package com.project.dine.right.dto;

import com.project.dine.right.dto.vo.PreferenceObjectVO;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
public class OnboardingUserSavePreferenceRequestDTO {

    private Long userId;

    private PreferenceObjectVO preferenceObject;

}
