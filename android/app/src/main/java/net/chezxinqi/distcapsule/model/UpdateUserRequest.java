package net.chezxinqi.distcapsule.model;

import com.google.gson.annotations.SerializedName;

public class UpdateUserRequest {
    @SerializedName("name")
    private final String name;
    @SerializedName("assigned_channel")
    private final Integer assignedChannel;

    public UpdateUserRequest(String name, Integer assignedChannel) {
        this.name = name;
        this.assignedChannel = assignedChannel;
    }
}
