package net.chezxinqi.distcapsule.model;

import com.google.gson.annotations.SerializedName;

public class EnrollUserResponse {
    @SerializedName("status")
    private String status;

    @SerializedName("user_id")
    private int userId;

    public String getStatus() {
        return status;
    }

    public int getUserId() {
        return userId;
    }
}
