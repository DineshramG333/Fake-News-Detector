package com.fakenews.model;

/**
 * Structured response returned by POST /api/detect to the React frontend.
 * Example:
 * {
 *   "label": "FAKE",
 *   "confidenceScore": 91.2,
 *   "text": "...",
 *   "timestamp": "2026-09-27T12:00:00Z",
 *   "probabilities": { "real": 8.8, "fake": 91.2 }
 * }
 */
public class DetectionResponse {

    private String label;
    private double confidenceScore;
    private String text;
    private String timestamp;
    private Probabilities probabilities;

    public DetectionResponse() {
    }

    public DetectionResponse(String label, double confidenceScore, String text, String timestamp,
                              Probabilities probabilities) {
        this.label = label;
        this.confidenceScore = confidenceScore;
        this.text = text;
        this.timestamp = timestamp;
        this.probabilities = probabilities;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public double getConfidenceScore() {
        return confidenceScore;
    }

    public void setConfidenceScore(double confidenceScore) {
        this.confidenceScore = confidenceScore;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public Probabilities getProbabilities() {
        return probabilities;
    }

    public void setProbabilities(Probabilities probabilities) {
        this.probabilities = probabilities;
    }

    /**
     * Nested breakdown of class probabilities, mirrors the Python service's
     * "probabilities" object but with lowercase keys for a cleaner frontend contract.
     */
    public static class Probabilities {
        private double real;
        private double fake;

        public Probabilities() {
        }

        public Probabilities(double real, double fake) {
            this.real = real;
            this.fake = fake;
        }

        public double getReal() {
            return real;
        }

        public void setReal(double real) {
            this.real = real;
        }

        public double getFake() {
            return fake;
        }

        public void setFake(double fake) {
            this.fake = fake;
        }
    }
}
