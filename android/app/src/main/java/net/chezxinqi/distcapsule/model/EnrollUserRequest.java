package net.chezxinqi.distcapsule.model;

import com.google.gson.annotations.SerializedName;

public class EnrollUserRequest {
    @SerializedName("name")
    private final String name;

    @SerializedName("auth_level")
    private final int authLevel;

    @SerializedName("assigned_channel")
    private final int assignedChannel;

    public EnrollUserRequest(String name, int authLevel, int assignedChannel) {
        this.name = name;
        this.authLevel = authLevel;
        this.assignedChannel = assignedChannel;
    }
}
