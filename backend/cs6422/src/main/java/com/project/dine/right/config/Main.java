package com.project.dine.right.config;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.data.web.SpringDataWebAutoConfiguration;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.data.jdbc.repository.config.EnableJdbcRepositories;

@SpringBootApplication(exclude = SpringDataWebAutoConfiguration.class)
@EnableJdbcRepositories(basePackages = {"com.project.dine.right.jdbc.repositories"})
@ComponentScan(basePackages = {"com.project.dine.right.*"})
public class Main {
    public static void main(String[] args) {
        SpringApplication.run(Main.class, args);
    }
}