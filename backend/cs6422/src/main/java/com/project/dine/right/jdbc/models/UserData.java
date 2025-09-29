package com.project.dine.right.jdbc.models;

import lombok.Getter;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

@Table("UserData")
public class UserData {

    @Id
    @Getter
    @Column("user_id")
    private Long userId;

    @Getter
    @Column("username")
    private String userName;

    @Getter
    @Column("email")
    private String email;

    @Getter
    @Column("password")
    private String password;
}
