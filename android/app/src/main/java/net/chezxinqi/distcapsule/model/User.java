package net.chezxinqi.distcapsule.model;

import com.google.gson.annotations.SerializedName;

public class User {
    @SerializedName(value = "user_id", alternate = {"id"})
    private int userId;

    @SerializedName("name")
    private String name;

    @SerializedName("auth_level")
    private int authLevel;

    @SerializedName("assigned_channel")
    private Integer assignedChannel;

    @SerializedName("has_face")
    private int hasFace;

    @SerializedName("has_fingerprint")
    private int hasFingerprint;

    @SerializedName("is_active")
    private int isActive;

    public User(int userId, String name, int authLevel, Integer assignedChannel, int hasFace, int hasFingerprint, int isActive) {
        this.userId = userId;
        this.name = name;
        this.authLevel = authLevel;
        this.assignedChannel = assignedChannel;
        this.hasFace = hasFace;
        this.hasFingerprint = hasFingerprint;
        this.isActive = isActive;
    }

    public int getId() {
        return userId;
    }

    public String getName() {
        return name;
    }

    public int getAuthLevel() {
        return authLevel;
    }

    public int getAssignedChannel() {
        return assignedChannel == null ? -1 : assignedChannel;
    }

    public Integer getAssignedChannelOrNull() {
        return assignedChannel;
    }

    public void setAssignedChannel(Integer channel) {
        this.assignedChannel = channel;
    }

    public boolean hasFace() {
        return hasFace == 1;
    }

    public boolean hasFingerprint() {
        return hasFingerprint == 1;
    }

    public void setHasFace(boolean value) {
        this.hasFace = value ? 1 : 0;
    }

    public void setHasFingerprint(boolean value) {
        this.hasFingerprint = value ? 1 : 0;
    }

    public boolean isActive() {
        return isActive == 1;
    }

    @Override
    public String toString() {
        String activeLabel = isActive() ? "actif" : "inactif";
        String channelLabel = assignedChannel == null ? "aucun canal" : "Canal " + assignedChannel;
        return userId + " - " + name + " (Niv " + authLevel + ", " + channelLabel + ", " + activeLabel + ")";
    }
}
