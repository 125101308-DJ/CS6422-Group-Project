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
@Table(schema = "public", name = "userdata")
public class UserData {

    @Id
    @Column("user_id")
    private Long userId;

    @Column("name")
    private String name;

    @Column("email")
    private String email;

    @Column("password")
    private String password;
}
