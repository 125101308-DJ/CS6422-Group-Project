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
@Table(schema = "public", name = "user_preferred_cuisines")
public class UserPreferredCuisines {

    @Id
    @Column("c_id")
    private String id;

    @Column("user_id")
    private Long userId;

    @Column("preferred_cuisines")
    private String preferredCuisines;
}
