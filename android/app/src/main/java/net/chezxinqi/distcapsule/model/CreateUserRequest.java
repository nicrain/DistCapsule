package net.chezxinqi.distcapsule.model;

import com.google.gson.annotations.SerializedName;

public class CreateUserRequest {
    @SerializedName("name")
    private final String name;
    @SerializedName("auth_level")
    private final int authLevel;
    @SerializedName("assigned_channel")
    private final Integer assignedChannel;

    public CreateUserRequest(String name, int authLevel, Integer assignedChannel) {
        this.name = name;
        this.authLevel = authLevel;
        this.assignedChannel = assignedChannel;
    }
}
