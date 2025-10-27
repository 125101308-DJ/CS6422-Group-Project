package com.project.dine.right.jdbc.models;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

@Getter
@Setter
@ToString
@Table(schema = "public", name = "userpreferences")
public class UserPreferences {

    @Id
    @Column("preference_id")
    private Long preferenceId;

    @Column("user_id")
    private Long userId;

    @Column("preferred_price_range")
    private String preferredPriceRange;

    @Column("preferred_location")
    private String preferredLocation;

    @Column("preferred_service")
    private String preferredService;
}
