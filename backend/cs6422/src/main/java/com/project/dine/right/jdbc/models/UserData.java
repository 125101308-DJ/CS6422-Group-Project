package com.project.dine.right.jdbc.models;

import lombok.Getter;
import lombok.Setter;
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
    @Setter
    @Column("username")
    private String userName;

    @Getter
    @Setter
    @Column("email")
    private String email;

    @Getter
    @Setter
    @Column("password")
    private String password;

    @Override
    public String toString() {
        return "UserData{" +
                "userId=" + userId +
                ", userName='" + userName + '\'' +
                ", email='" + email + '\'' +
                ", password='" + password + '\'' +
                '}';
    }
}
