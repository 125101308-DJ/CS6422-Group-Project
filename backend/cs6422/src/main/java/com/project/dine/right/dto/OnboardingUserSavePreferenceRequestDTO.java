package com.project.dine.right.dto;

import com.project.dine.right.dto.vo.PreferenceObjectVO;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class OnboardingUserSavePreferenceRequestDTO {

    private Long userId;

    private PreferenceObjectVO preferenceObject;

}
