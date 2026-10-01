package com.fakenews.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Incoming request payload for POST /api/detect.
 * Example: { "text": "article content..." }
 */
public class DetectionRequest {

    @NotBlank(message = "Text must not be blank")
    @Size(min = 1, max = 20000, message = "Text must be between 1 and 20000 characters")
    private String text;

    public DetectionRequest() {
    }

    public DetectionRequest(String text) {
        this.text = text;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }
}
