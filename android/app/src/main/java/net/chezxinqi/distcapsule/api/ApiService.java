package net.chezxinqi.distcapsule.api;

import java.util.List;

import net.chezxinqi.distcapsule.model.AuthRequest;
import net.chezxinqi.distcapsule.model.BindRequest;
import net.chezxinqi.distcapsule.model.CreateUserRequest;
import net.chezxinqi.distcapsule.model.LogEntry;
import net.chezxinqi.distcapsule.model.StatusResponse;
import net.chezxinqi.distcapsule.model.UpdateUserRequest;
import net.chezxinqi.distcapsule.model.User;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.DELETE;
import retrofit2.http.GET;
import retrofit2.http.PATCH;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface ApiService {

    @GET("users")
    Call<List<User>> getUsers();

    @POST("users")
    Call<User> createUser(@Body CreateUserRequest request);

    @PATCH("users/{user_id}")
    Call<User> updateUser(@Path("user_id") int userId, @Body UpdateUserRequest request);

    @DELETE("users/{user_id}")
    Call<StatusResponse> deleteUser(@Path("user_id") int userId);

    @POST("command/enroll_face")
    Call<StatusResponse> enrollFace(@Query("user_id") int userId);

    @POST("command/enroll_finger")
    Call<StatusResponse> enrollFinger(@Query("user_id") int userId, @Query("finger_label") String fingerLabel);

    @POST("command/unlock")
    Call<StatusResponse> unlock(@Query("channel") int channel);

    @POST("bind")
    Call<StatusResponse> bindDevice(@Body BindRequest request);

    @POST("auth")
    Call<User> auth(@Body AuthRequest request);

    @GET("logs")
    Call<List<LogEntry>> getLogs(@Query("limit") int limit);
}
