package com.project.dine.right.controller;

import com.project.dine.right.dto.DashboardRestaurantsDataResponseDTO;
import com.project.dine.right.enums.CustomErrorCodes;
import com.project.dine.right.interfaces.IDashboardService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class DashboardController {

    @Autowired
    private IDashboardService dashboardService;

    @GetMapping("/getAllRestaurantsData")
    public ResponseEntity<DashboardRestaurantsDataResponseDTO> getRestaurantsData() {

        var responseDTO = new DashboardRestaurantsDataResponseDTO();

        var restaurants = dashboardService.getRestaurants();

        responseDTO.setRestaurantData(restaurants);
        responseDTO.setCode(CustomErrorCodes.SUCCESS.name());
        return ResponseEntity.ok().body(responseDTO);
    }
}
