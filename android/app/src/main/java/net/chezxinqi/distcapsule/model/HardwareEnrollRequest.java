package net.chezxinqi.distcapsule.model;

import com.google.gson.annotations.SerializedName;

public class HardwareEnrollRequest {
    @SerializedName("user_id")
    private final int userId;

    public HardwareEnrollRequest(int userId) {
        this.userId = userId;
    }
}
