package com.project.dine.right.jdbc.models;

import lombok.Getter;
import lombok.Setter;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

@Getter
@Setter
@Table("user_preferred_cuisines")
public class UserPreferredCuisines {

    @Column("user_id")
    private Long userId;

    @Column("preferred_cuisines")
    private String preferredCuisines;

    @Override
    public String toString() {
        return "UserPreferredCuisines{" +
                "userId=" + userId +
                ", preferredCuisines='" + preferredCuisines + '\'' +
                '}';
    }
}
