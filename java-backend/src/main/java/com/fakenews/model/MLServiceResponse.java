package com.fakenews.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.Map;

/**
 * Maps the JSON body returned by the Python ML service's POST /predict endpoint:
 * {
 *   "label": "REAL" | "FAKE",
 *   "confidence": 87.42,
 *   "probabilities": { "REAL": 12.58, "FAKE": 87.42 },
 *   "timestamp": "2026-09-27T12:00:00+00:00"
 * }
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class MLServiceResponse {

    private String label;
    private double confidence;
    private Map<String, Double> probabilities;
    private String timestamp;

    public MLServiceResponse() {
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public Map<String, Double> getProbabilities() {
        return probabilities;
    }

    public void setProbabilities(Map<String, Double> probabilities) {
        this.probabilities = probabilities;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }
}
