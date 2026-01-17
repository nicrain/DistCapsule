package net.chezxinqi.distcapsule.model;

import com.google.gson.annotations.SerializedName;

public class LogEntry {
    @SerializedName("timestamp")
    private String timestamp;

    @SerializedName("user_id")
    private int userId;

    @SerializedName("event_type")
    private String eventType;

    @SerializedName("status")
    private String status;

    public String getTimestamp() {
        return timestamp;
    }

    public int getUserId() {
        return userId;
    }

    public String getEventType() {
        return eventType;
    }

    public String getStatus() {
        return status;
    }

    @Override
    public String toString() {
        return timestamp + " | utilisateur=" + userId + " | " + eventType + " | " + status;
    }
}
