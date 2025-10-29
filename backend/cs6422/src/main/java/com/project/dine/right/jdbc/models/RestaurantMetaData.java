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
@Table(schema = "public", name = "restaurant_metadata")
public class RestaurantMetaData {

    @Id
    @Column("place_id")
    private Long placeId;

    @Column("name")
    private String name;

    @Column("restaurant_type")
    private String restaurantType;

    @Column("cuisine_type")
    private String cuisineType;

    @Column("address")
    private String address;

    @Column("country")
    private String country;

    @Column("rating")
    private Float rating;

    @Column("review_count")
    private Long reviewCount;

    @Column("price_range")
    private String priceRange;

    @Column("phone")
    private String phone;

    @Column("website")
    private String website;

    @Column("atmosphere")
    private String atmosphere;

    @Column("dietary_options")
    private String dietaryOptions;

    @Column("service_options")
    private String serviceOptions;

    @Column("amenities")
    private String amenities;

}
