package com.fakenews.service;

import com.fakenews.model.DetectionResponse;
import com.fakenews.model.MLServiceResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * Integration layer responsible for calling the Python ML service and
 * translating its response into the DetectionResponse contract exposed
 * to the frontend by DetectorController.
 */
@Service
public class MLIntegrationService {

    private final RestTemplate restTemplate;

    @Value("${ml.service.url:http://localhost:5000/predict}")
    private String mlServiceUrl;

    public MLIntegrationService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public DetectionResponse analyzeText(String text) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> requestBody = new HashMap<>();
        requestBody.put("text", text);

        HttpEntity<Map<String, String>> requestEntity = new HttpEntity<>(requestBody, headers);

        try {
            ResponseEntity<MLServiceResponse> response = restTemplate.postForEntity(
                    mlServiceUrl, requestEntity, MLServiceResponse.class
            );

            MLServiceResponse mlResponse = response.getBody();
            if (mlResponse == null) {
                throw new MLServiceUnavailableException(
                        "The ML service returned an empty response.", null
                );
            }

            DetectionResponse.Probabilities probabilities = null;
            if (mlResponse.getProbabilities() != null) {
                probabilities = new DetectionResponse.Probabilities(
                        mlResponse.getProbabilities().getOrDefault("REAL", 0.0),
                        mlResponse.getProbabilities().getOrDefault("FAKE", 0.0)
                );
            }

            return new DetectionResponse(
                    mlResponse.getLabel(),
                    mlResponse.getConfidence(),
                    text,
                    Instant.now().toString(),
                    probabilities
            );

        } catch (ResourceAccessException e) {
            // Connection refused / timeout - the Python service is likely not running.
            throw new MLServiceUnavailableException(
                    "Unable to reach the ML service at " + mlServiceUrl
                            + ". Ensure the Python service is running on port 5000.",
                    e
            );
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            throw new MLServiceUnavailableException(
                    "The ML service rejected the request: " + e.getStatusCode() + " - " + e.getResponseBodyAsString(),
                    e
            );
        }
    }

    /**
     * Thrown whenever the Python ML service cannot be reached or returns an error.
     * Caught by DetectorController and translated into a 503 response.
     */
    public static class MLServiceUnavailableException extends RuntimeException {
        public MLServiceUnavailableException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
