package com.project.dine.right.jdbc.models;

import lombok.Getter;
import lombok.Setter;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

@Getter
@Setter
@Table("user_preferred_ambience")
public class UserPreferredAmbience {

    @Column("user_id")
    private Long userId;

    @Column("preferred_ambience")
    private String preferredAmbience;

    @Override
    public String toString() {
        return "UserPreferredAmbience{" +
                "userId=" + userId +
                ", preferredAmbience='" + preferredAmbience + '\'' +
                '}';
    }
}
