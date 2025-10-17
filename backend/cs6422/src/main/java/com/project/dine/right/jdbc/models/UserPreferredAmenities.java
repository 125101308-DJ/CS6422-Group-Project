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
@Table(schema = "public", name = "user_preferred_amenities")
public class UserPreferredAmenities {

    @Id
    @Column("a_id")
    private Long id;

    @Column("user_id")
    private Long userId;

    @Column("preferred_amenities")
    private String preferredAmenities;
}
