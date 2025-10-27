package com.project.dine.right.jdbc.models;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

@ToString
@Getter
@Setter
@Table(schema = "public", name = "top_restaurants")
public class TopRestaurants {

    @Id
    @Column("k_id")
    private Long id;

    @Column("place_id")
    private Long placeId;

    @Column("user_id")
    private Long userId;

    @Column("rank")
    private Integer rank;
}
