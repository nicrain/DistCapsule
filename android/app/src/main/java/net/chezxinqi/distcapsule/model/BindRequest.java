package net.chezxinqi.distcapsule.model;

import com.google.gson.annotations.SerializedName;

public class BindRequest {
    @SerializedName("user_id")
    private final int userId;
    @SerializedName("token")
    private final String token;

    public BindRequest(int userId, String token) {
        this.userId = userId;
        this.token = token;
    }
}
