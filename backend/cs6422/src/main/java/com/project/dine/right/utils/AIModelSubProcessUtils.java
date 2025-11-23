package com.project.dine.right.utils;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.dine.right.dto.AIModelRequestDTO;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.List;

@Service
public class AIModelSubProcessUtils {

    private static final ObjectMapper mapper = new ObjectMapper();
    private static Process process;
    private static String inferenceFilePath;
    private static String envPath;
    @Value("${model.env.path}")
    private String env;
    @Value("${model.inf.file.path}")
    private String inference;
    @Value("${model.results.limit}")
    private Long resultLimit;
    @Value("${model.results.key}")
    private String resultsKey;

    private static synchronized Process getProcess() {
        try {
            if (process == null || !process.isAlive()) {
                var processBuilder = new ProcessBuilder(envPath, inferenceFilePath);
                processBuilder.redirectErrorStream(true);
                process = processBuilder.start();
            }
        } catch (Exception ignored) {
        }
        return process;
    }

    @PostConstruct
    public void init() {
        inferenceFilePath = inference;
        envPath = env;
    }

    public List<Long> getRecommendations(AIModelRequestDTO aiModelRequestDTO) {

        try {

            aiModelRequestDTO.setN(resultLimit);

            var process = getProcess();

            try (var outputStream = process.getOutputStream()) {
                mapper.writeValue(outputStream, aiModelRequestDTO);
            }

            var output = new StringBuilder();
            try (var reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line);
                }
            }

            return mapper.convertValue(mapper.readTree(output.toString()).get(resultsKey), new TypeReference<>() {
            });

        } catch (Exception ignored) {
        }

        return null;
    }
}
