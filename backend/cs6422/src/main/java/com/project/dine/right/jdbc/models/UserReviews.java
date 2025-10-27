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
@Table(schema = "public", name = "user_reviews")
public class UserReviews {

    @Id
    @Column("r_id")
    private Long id;

    @Column("place_id")
    private Long placeId;

    @Column("username")
    private String username;

    @Column("user_review_id")
    private Long userReviewsId;

    @Column("review_date")
    private String reviewDate;

    @Column("rating")
    private Short rating;

    @Column("review_text")
    private String reviewText;
}
