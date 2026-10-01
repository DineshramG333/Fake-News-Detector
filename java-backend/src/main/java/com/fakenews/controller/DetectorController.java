package com.fakenews.controller;

import com.fakenews.model.DetectionRequest;
import com.fakenews.model.DetectionResponse;
import com.fakenews.service.MLIntegrationService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * Core REST API consumed by the React frontend.
 *
 * POST /api/detect  { "text": "article content..." }
 *   -> forwards the text to the Python ML service and returns a
 *      structured DetectionResponse (label, confidenceScore, text, timestamp).
 */
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class DetectorController {

    private final MLIntegrationService mlIntegrationService;

    public DetectorController(MLIntegrationService mlIntegrationService) {
        this.mlIntegrationService = mlIntegrationService;
    }

    @PostMapping("/detect")
    public ResponseEntity<?> detect(@Valid @RequestBody DetectionRequest request) {
        try {
            DetectionResponse response = mlIntegrationService.analyzeText(request.getText());
            return ResponseEntity.ok(response);
        } catch (MLIntegrationService.MLServiceUnavailableException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(error);
        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Unexpected error while analyzing text: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> status = new HashMap<>();
        status.put("status", "UP");
        status.put("service", "fake-news-detector-api-gateway");
        return ResponseEntity.ok(status);
    }

    /**
     * Converts bean validation failures (e.g. blank "text" field) into a clean 400 response
     * instead of Spring's default verbose validation error payload.
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidationErrors(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .findFirst()
                .map(fieldError -> fieldError.getDefaultMessage())
                .orElse("Invalid request payload");

        Map<String, String> error = new HashMap<>();
        error.put("error", message);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }
}
