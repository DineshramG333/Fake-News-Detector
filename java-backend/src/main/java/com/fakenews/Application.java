package com.fakenews;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

/**
 * Entry point for the Fake News Detector API Gateway / Core Service.
 *
 * This Spring Boot application:
 *  - Exposes REST endpoints consumed by the React frontend.
 *  - Forwards article text to the Python ML microservice for inference.
 *  - Shapes and returns a structured response (label, confidenceScore, text, timestamp).
 */
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    /**
     * RestTemplate bean used by MLIntegrationService to call the Python ML service.
     * A fixed connect/read timeout keeps a slow or unreachable ML service from
     * hanging requests indefinitely.
     */
    @Bean
    public RestTemplate restTemplate(org.springframework.boot.web.client.RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(java.time.Duration.ofSeconds(5))
                .setReadTimeout(java.time.Duration.ofSeconds(10))
                .build();
    }
}
