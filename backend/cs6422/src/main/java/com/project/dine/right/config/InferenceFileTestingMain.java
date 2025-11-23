package com.project.dine.right.config;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;

public class InferenceFileTestingMain {

    private static final ObjectMapper mapper = new ObjectMapper();

    public static void main(String[] args) throws IOException, InterruptedException {
        ProcessBuilder processBuilder = new ProcessBuilder("python/venv/bin/python", "src/main/resources/inference.py");
        processBuilder.redirectErrorStream(true);
        Process process = processBuilder.start();

        //AIModelRequestDTO(address=Cork City Centre, Cork, Ireland, radiusKm=5, cuisineType=[Continental, Sweet and Savory], budgetFilter=1, atmosphereFilter=[Casual], amenitiesFilter=[Bar], restaurantTypeFilter=[Street Food, Bistro], n=10)

        String a = """
                {
                        "address": "Cork City Centre, Cork, Ireland",
                        "radius_km": 5,
                        "cuisine_type": ["Continental"],
                        "budget_filter": 2,
                        "atmosphere_filter": ["Casual"],
                        "amenities_filter": ["Bar"],
                        "restaurant_type_filter": ["Restaurant"],
                        "n": 10
                    }""";
        Map<String, Object> b = mapper.readValue(a, HashMap.class);

        try (OutputStream outputStream = process.getOutputStream()) {
            mapper.writeValue(outputStream, b);
        }

        try (BufferedReader errReader = new BufferedReader(new InputStreamReader(process.getErrorStream()))) {
            errReader.lines().forEach(System.err::println);
        }

        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
        }

        // Wait for the process to finish

        //JsonNode node = mapper.readTree(output.toString());


        System.out.println(output);
    }

}
