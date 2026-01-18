package net.chezxinqi.distcapsule;

import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.animation.OvershootInterpolator;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

import com.google.android.material.dialog.MaterialAlertDialogBuilder;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.textfield.TextInputLayout;

import net.chezxinqi.distcapsule.api.ApiClient;
import net.chezxinqi.distcapsule.api.ApiService;
import net.chezxinqi.distcapsule.model.AuthRequest;
import net.chezxinqi.distcapsule.model.BindRequest;
import net.chezxinqi.distcapsule.model.CreateUserRequest;
import net.chezxinqi.distcapsule.model.StatusResponse;
import net.chezxinqi.distcapsule.model.UpdateUserRequest;
import net.chezxinqi.distcapsule.model.User;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

@SuppressWarnings("deprecation")
public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "distcapsule_prefs";
    private static final String KEY_BASE_URL = "base_url";
    private static final String KEY_TOKEN = "auth_token";
    private static final String DEFAULT_IP = "192.168.4.1";
    private static final long CHANNEL_MAP_REFRESH_MS = 10000;

    private EditText etBaseUrl;
    private TextInputLayout tilBaseUrl;
    private boolean baseUrlEditing = false;
    // ...

    // ... (in onCreate)
        btnAdminHardwareBack.setOnClickListener(v -> showAdminMenu());

        setupBaseUrlEditing();
        String savedUrl = loadBaseUrl();
        if (savedUrl.isEmpty()) {
            etBaseUrl.setText(DEFAULT_IP);
        } else {
            etBaseUrl.setText(stripProtocolAndPort(savedUrl));
        }
        setBaseUrlEditable(false);
        showConnectionStep();
        playSplash();
        setupDebugScreenToggle();
    }

    private String stripProtocolAndPort(String url) {
        if (url == null) return "";
        String clean = url.replace("http://", "").replace("https://", "");
        if (clean.endsWith("/")) clean = clean.substring(0, clean.length() - 1);
        if (clean.contains(":8000")) {
            clean = clean.replace(":8000", "");
        }
        return clean;
    }

    private void setupAdapters() {
        bindAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, new ArrayList<>());
        etSelectUser.setAdapter(bindAdapter);
        setupDropdown(etSelectUser);
        etSelectUser.setOnItemClickListener((parent, view, position, id) -> {
            if (position >= 0 && position < bindUsers.size()) {
                selectedBindUser = bindUsers.get(position);
            }
        });

        adminAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, new ArrayList<>());
        etAdminSelectUser.setAdapter(adminAdapter);
        setupDropdown(etAdminSelectUser);
        etAdminSelectUser.setOnItemClickListener((parent, view, position, id) -> {
            if (position >= 0 && position < adminUsers.size()) {
                selectedAdminUser = adminUsers.get(position);
                updateAdminUi(selectedAdminUser);
            }
        });

        etAdminDeleteUser.setAdapter(adminAdapter);
        setupDropdown(etAdminDeleteUser);
        etAdminDeleteUser.setOnItemClickListener((parent, view, position, id) -> {
            if (position >= 0 && position < adminUsers.size()) {
                selectedDeleteUser = adminUsers.get(position);
            }
        });
    }

    private void connectToApi() {
        if (demoMode) {
            Toast.makeText(this, getString(R.string.toast_demo_enabled), Toast.LENGTH_SHORT).show();
            showBindStep();
            return;
        }
        String input = etBaseUrl.getText() == null ? "" : etBaseUrl.getText().toString().trim();
        String normalizedUrl = normalizeBaseUrlOrEmpty(input);
        if (normalizedUrl.isEmpty()) {
            normalizedUrl = resolveBaseUrl();
        }
        if (normalizedUrl.isEmpty()) {
            Toast.makeText(this, getString(R.string.toast_base_url_required), Toast.LENGTH_SHORT).show();
            return;
        }

        saveBaseUrl(normalizedUrl);
        etBaseUrl.setText(normalizedUrl);
        setBaseUrlEditable(false);

        final String baseUrl = normalizedUrl;
        ApiService api = apiForBaseUrl(baseUrl);

        setLoading(true);
        String token = loadToken();
        if (!token.isEmpty()) {
            api.auth(new AuthRequest(token)).enqueue(new Callback<User>() {
                @Override
                public void onResponse(Call<User> call, Response<User> response) {
                    setLoading(false);
                    if (!response.isSuccessful() || response.body() == null) {
                        clearToken();
                        loadUsersForBind(baseUrl);
                        Toast.makeText(MainActivity.this, getString(R.string.toast_auth_failed), Toast.LENGTH_SHORT).show();
                        return;
                    }
                    currentUser = response.body();
                    showDashboardStep();
                    refreshUsers(baseUrl);
                }

                @Override
                public void onFailure(Call<User> call, Throwable t) {
                    setLoading(false);
                    Toast.makeText(MainActivity.this, getString(R.string.toast_auth_failed), Toast.LENGTH_SHORT).show();
                }
            });
        } else {
            loadUsersForBind(baseUrl);
        }
    }

    private void loadUsersForBind(String baseUrl) {
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.getUsers().enqueue(new Callback<List<User>>() {
            @Override
            public void onResponse(Call<List<User>> call, Response<List<User>> response) {
                setLoading(false);
                if (!response.isSuccessful() || response.body() == null) {
                    Toast.makeText(MainActivity.this, getString(R.string.toast_auth_failed), Toast.LENGTH_SHORT).show();
                    return;
                }
                cachedUsers.clear();
                cachedUsers.addAll(response.body());
                updateUserAdapters();
                showBindStep();
            }

            @Override
            public void onFailure(Call<List<User>> call, Throwable t) {
                setLoading(false);
                Toast.makeText(MainActivity.this, getString(R.string.toast_auth_failed), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void refreshUsers(String baseUrl) {
        ApiService api = apiForBaseUrl(baseUrl);
        api.getUsers().enqueue(new Callback<List<User>>() {
            @Override
            public void onResponse(Call<List<User>> call, Response<List<User>> response) {
                if (!response.isSuccessful() || response.body() == null) {
                    return;
                }
                cachedUsers.clear();
                cachedUsers.addAll(response.body());
                updateUserAdapters();
                syncCurrentUserFromCache();
            }

            @Override
            public void onFailure(Call<List<User>> call, Throwable t) {
            }
        });
    }

    private void scheduleUserRefresh(String baseUrl) {
        if (baseUrl == null || baseUrl.isEmpty()) {
            return;
        }
        new Handler(Looper.getMainLooper()).postDelayed(() -> refreshUsers(baseUrl), 2500);
    }

    private void updateUserAdapters() {
        bindUsers.clear();
        adminUsers.clear();
        List<String> bindLabels = new ArrayList<>();
        List<String> adminLabels = new ArrayList<>();
        User matchedBind = null;
        User matchedAdmin = null;
        User matchedDelete = null;
        for (User user : cachedUsers) {
            String label = user.getId() + " - " + user.getName();
            bindUsers.add(user);
            adminUsers.add(user);
            bindLabels.add(label);
            adminLabels.add(label);
            if (selectedBindUser != null && user.getId() == selectedBindUser.getId()) {
                matchedBind = user;
            }
            if (selectedAdminUser != null && user.getId() == selectedAdminUser.getId()) {
                matchedAdmin = user;
            }
            if (selectedDeleteUser != null && user.getId() == selectedDeleteUser.getId()) {
                matchedDelete = user;
            }
        }
        selectedBindUser = matchedBind;
        selectedAdminUser = matchedAdmin;
        selectedDeleteUser = matchedDelete;
        bindAdapter.clear();
        bindAdapter.addAll(bindLabels);
        bindAdapter.notifyDataSetChanged();
        adminAdapter.clear();
        adminAdapter.addAll(adminLabels);
        adminAdapter.notifyDataSetChanged();
        updateChannelMap();
    }

    private void bindSelectedUser() {
        if (demoMode) {
            if (selectedBindUser == null) {
                Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
                return;
            }
            currentUser = selectedBindUser;
            showDashboardStep();
            return;
        }
        if (selectedBindUser == null) {
            Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) {
            Toast.makeText(this, getString(R.string.toast_base_url_required), Toast.LENGTH_SHORT).show();
            return;
        }

        String token = UUID.randomUUID().toString();
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.bindDevice(new BindRequest(selectedBindUser.getId(), token)).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    Toast.makeText(MainActivity.this, getString(R.string.toast_bind_failed), Toast.LENGTH_SHORT).show();
                    return;
                }
                saveToken(token);
                currentUser = selectedBindUser;
                Toast.makeText(MainActivity.this, getString(R.string.toast_bind_success), Toast.LENGTH_SHORT).show();
                showDashboardStep();
                refreshUsers(baseUrl);
            }

            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                Toast.makeText(MainActivity.this, getString(R.string.toast_bind_failed), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void createUser() {
        String name = etCreateName.getText() == null ? "" : etCreateName.getText().toString().trim();
        if (name.isEmpty()) {
            Toast.makeText(this, getString(R.string.toast_field_required, getString(R.string.field_name)), Toast.LENGTH_SHORT).show();
            return;
        }
        String authText = etCreateAuthLevel.getText() == null ? "" : etCreateAuthLevel.getText().toString().trim();
        if (authText.isEmpty()) {
            Toast.makeText(this, getString(R.string.toast_field_required, getString(R.string.field_auth_level)), Toast.LENGTH_SHORT).show();
            return;
        }
        int authLevel;
        try {
            authLevel = Integer.parseInt(authText);
        } catch (NumberFormatException e) {
            Toast.makeText(this, getString(R.string.toast_field_number, getString(R.string.field_auth_level)), Toast.LENGTH_SHORT).show();
            return;
        }
        if (authLevel != 1 && authLevel != 2) {
            Toast.makeText(this, getString(R.string.toast_auth_level_invalid), Toast.LENGTH_SHORT).show();
            return;
        }
        String channelText = etCreateChannel.getText() == null ? "" : etCreateChannel.getText().toString().trim();
        Integer channel = null;
        if (!channelText.isEmpty()) {
            try {
                channel = Integer.parseInt(channelText);
            } catch (NumberFormatException e) {
                Toast.makeText(this, getString(R.string.toast_field_number, getString(R.string.field_channel)), Toast.LENGTH_SHORT).show();
                return;
            }
        }
        if (demoMode) {
            int nextId = 1;
            for (User user : cachedUsers) {
                nextId = Math.max(nextId, user.getId() + 1);
            }
            cachedUsers.add(new User(nextId, name, authLevel, channel, 0, 0, 1));
            updateUserAdapters();
            clearCreateUserFields();
            Toast.makeText(this, getString(R.string.toast_user_created), Toast.LENGTH_SHORT).show();
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.createUser(new CreateUserRequest(name, authLevel, channel)).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    showHttpError(response.code());
                    return;
                }
                Toast.makeText(MainActivity.this, getString(R.string.toast_user_created), Toast.LENGTH_SHORT).show();
                clearCreateUserFields();
                refreshUsers(baseUrl);
            }

            @Override
            public void onFailure(Call<User> call, Throwable t) {
                setLoading(false);
                showNetworkError();
            }
        });
    }

    private void clearCreateUserFields() {
        etCreateName.setText("");
        etCreateAuthLevel.setText("");
        etCreateChannel.setText("");
    }

    private void unlockChannel() {
        if (currentUser == null) {
            return;
        }
        if (demoMode) {
            if (currentUser.getAssignedChannel() > 0) {
                showResultDialog(R.string.action_unlock_title, R.string.action_unlock_detail);
            } else {
                Toast.makeText(this, getString(R.string.toast_unlock_unavailable), Toast.LENGTH_SHORT).show();
            }
            return;
        }
        int channel = currentUser.getAssignedChannel();
        if (channel <= 0) {
            Toast.makeText(this, getString(R.string.toast_unlock_unavailable), Toast.LENGTH_SHORT).show();
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.unlock(channel).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    showHttpError(response.code());
                    return;
                }
                Toast.makeText(MainActivity.this, getString(R.string.toast_unlock_success), Toast.LENGTH_SHORT).show();
                showResultDialog(R.string.action_unlock_title, R.string.action_unlock_detail);
            }

            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                showNetworkError();
            }
        });
    }

    private void updateBiometric(boolean face) {
        if (demoMode) {
            if (currentUser == null) {
                return;
            }
            if (face) {
                currentUser.setHasFace(true);
            } else {
                currentUser.setHasFingerprint(true);
            }
            updateDashboardUi(currentUser);
            Toast.makeText(this, getString(R.string.toast_enroll_started), Toast.LENGTH_SHORT).show();
            showActionResult(
                    face ? R.string.action_enroll_face_title : R.string.action_enroll_finger_title,
                    face ? R.string.action_enroll_face_detail : R.string.action_enroll_finger_detail
            );
            return;
        }
        if (currentUser == null) {
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        Toast.makeText(this, getString(R.string.toast_enroll_started), Toast.LENGTH_SHORT).show();
        Call<StatusResponse> call = face ? api.enrollFace(currentUser.getId()) : api.enrollFinger(currentUser.getId());
        call.enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    showHttpError(response.code());
                    return;
                }
                refreshUsers(baseUrl);
                scheduleUserRefresh(baseUrl);
                showActionResult(
                        face ? R.string.action_enroll_face_title : R.string.action_enroll_finger_title,
                        face ? R.string.action_enroll_face_detail : R.string.action_enroll_finger_detail
                );
            }

            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                showNetworkError();
            }
        });
    }

    private void updateAdminBiometric(boolean face) {
        if (demoMode) {
            if (selectedAdminUser == null) {
                Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
                return;
            }
            if (face) {
                selectedAdminUser.setHasFace(true);
            } else {
                selectedAdminUser.setHasFingerprint(true);
            }
            updateAdminUi(selectedAdminUser);
            Toast.makeText(this, getString(R.string.toast_enroll_started), Toast.LENGTH_SHORT).show();
            showActionResult(
                    face ? R.string.action_enroll_face_title : R.string.action_enroll_finger_title,
                    face ? R.string.action_enroll_face_detail : R.string.action_enroll_finger_detail
            );
            return;
        }
        if (selectedAdminUser == null) {
            Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        Toast.makeText(this, getString(R.string.toast_enroll_started), Toast.LENGTH_SHORT).show();
        Call<StatusResponse> call = face ? api.enrollFace(selectedAdminUser.getId()) : api.enrollFinger(selectedAdminUser.getId());
        call.enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    showHttpError(response.code());
                    return;
                }
                refreshUsers(baseUrl);
                scheduleUserRefresh(baseUrl);
                showActionResult(
                        face ? R.string.action_enroll_face_title : R.string.action_enroll_finger_title,
                        face ? R.string.action_enroll_face_detail : R.string.action_enroll_finger_detail
                );
            }

            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                showNetworkError();
            }
        });
    }

    private void deleteCurrentUser() {
        if (demoMode) {
            currentUser = null;
            showBindStep();
            showDeletedDialog();
            return;
        }
        if (currentUser == null) {
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.deleteUser(currentUser.getId()).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    showHttpError(response.code());
                    return;
                }
                Toast.makeText(MainActivity.this, getString(R.string.toast_user_deleted), Toast.LENGTH_SHORT).show();
                clearToken();
                currentUser = null;
                showBindStep();
                showDeletedDialog();
                refreshUsers(baseUrl);
            }

            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                showNetworkError();
            }
        });
    }

    private void deleteAdminUser() {
        if (demoMode) {
            if (selectedDeleteUser == null) {
                Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
                return;
            }
            cachedUsers.removeIf(user -> user.getId() == selectedDeleteUser.getId());
            selectedDeleteUser = null;
            etAdminDeleteUser.setText("");
            updateUserAdapters();
            showActionResult(R.string.action_delete_title, R.string.action_delete_detail);
            return;
        }
        if (selectedDeleteUser == null) {
            Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.deleteUser(selectedDeleteUser.getId()).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    showHttpError(response.code());
                    return;
                }
                Toast.makeText(MainActivity.this, getString(R.string.toast_user_deleted), Toast.LENGTH_SHORT).show();
                selectedDeleteUser = null;
                etAdminDeleteUser.setText("");
                refreshUsers(baseUrl);
                showActionResult(R.string.action_delete_title, R.string.action_delete_detail);
            }

            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                showNetworkError();
            }
        });
    }

    private void assignAdminChannel() {
        if (selectedAdminUser == null) {
            Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
            return;
        }
        String text = etAdminChannel.getText().toString().trim();
        Integer channel = null;
        if (!text.isEmpty()) {
            try {
                channel = Integer.parseInt(text);
            } catch (NumberFormatException e) {
                Toast.makeText(this, getString(R.string.toast_field_number, getString(R.string.field_channel)), Toast.LENGTH_SHORT).show();
                return;
            }
        }
        if (demoMode) {
            selectedAdminUser.setAssignedChannel(channel);
            updateAdminUi(selectedAdminUser);
            if (currentUser != null && currentUser.getId() == selectedAdminUser.getId()) {
                updateDashboardUi(currentUser);
            } else {
                updateChannelMap();
            }
            Toast.makeText(this, getString(R.string.toast_channel_updated), Toast.LENGTH_SHORT).show();
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.updateUser(selectedAdminUser.getId(), new UpdateUserRequest(null, channel)).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    if (response.code() == 400) {
                        Toast.makeText(MainActivity.this, getString(R.string.toast_channel_occupied), Toast.LENGTH_SHORT).show();
                    } else {
                        showHttpError(response.code());
                    }
                    return;
                }
                Toast.makeText(MainActivity.this, getString(R.string.toast_channel_updated), Toast.LENGTH_SHORT).show();
                refreshUsers(baseUrl);
            }

            @Override
            public void onFailure(Call<User> call, Throwable t) {
                setLoading(false);
                showNetworkError();
            }
        });
    }

    private void unlockSpecificChannel(int channel) {
        if (demoMode) {
            showActionResult(R.string.action_unlock_title, R.string.action_unlock_detail);
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.unlock(channel).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    showHttpError(response.code());
                    return;
                }
                showActionResult(R.string.action_unlock_title, R.string.action_unlock_detail);
            }

            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                showNetworkError();
            }
        });
    }

    private void syncCurrentUserFromCache() {
        if (currentUser == null) {
            return;
        }
        User matchedCurrent = null;
        User matchedAdmin = null;
        for (User user : cachedUsers) {
            if (user.getId() == currentUser.getId()) {
                matchedCurrent = user;
            }
            if (selectedAdminUser != null && user.getId() == selectedAdminUser.getId()) {
                matchedAdmin = user;
            }
        }
        if (matchedCurrent != null) {
            currentUser = matchedCurrent;
            updateDashboardUi(matchedCurrent);
        }
        if (matchedAdmin != null) {
            selectedAdminUser = matchedAdmin;
            updateAdminUi(matchedAdmin);
        }
    }

    private void updateDashboardUi(User user) {
        String greeting = "Bonjour, " + user.getName();
        tvGreeting.setText(greeting);
        tvGreeting.setVisibility(View.VISIBLE);

        String summary = buildBioSummary(user);
        tvBioSummary.setText(summary);

        String faceText = user.hasFace() ? getString(R.string.bio_face_ready) : getString(R.string.bio_face_pending);
        String fingerText = user.hasFingerprint() ? getString(R.string.bio_finger_ready) : getString(R.string.bio_finger_pending);
        tvFaceStatus.setText(faceText);
        tvFingerStatus.setText(fingerText);

        boolean isAdmin = user.getAuthLevel() == 1;
        // standard user does not show direct biometric buttons on this card
        if (!isAdmin) {
            btnDeleteUser.setText(R.string.button_delete_self);
        } else {
            btnDeleteUser.setText(R.string.button_delete_user);
        }

        boolean hasChannel = user.getAssignedChannel() > 0;
        btnUnlock.setEnabled(hasChannel);
        btnUnlock.setText(R.string.button_unlock);
        if (hasChannel) {
            tvChannelStatus.setText(getString(R.string.channel_status_assigned, user.getAssignedChannel()));
        } else {
            tvChannelStatus.setText(getString(R.string.channel_status_placeholder));
        }
        updateChannelMap();
    }

    private void updateAdminUi(User user) {
        if (user == null) {
            return;
        }
        String faceText = user.hasFace() ? getString(R.string.bio_face_ready) : getString(R.string.bio_face_pending);
        String fingerText = user.hasFingerprint() ? getString(R.string.bio_finger_ready) : getString(R.string.bio_finger_pending);
        tvAdminFaceStatus.setText(faceText);
        tvAdminFingerStatus.setText(fingerText);
        Integer channel = user.getAssignedChannelOrNull();
        etAdminChannel.setText(channel == null ? "" : String.valueOf(channel));
        btnAdminEnrollFace.setText(user.hasFace() ? R.string.button_update_face : R.string.button_enroll_face);
        btnAdminEnrollFinger.setText(user.hasFingerprint() ? R.string.button_update_finger : R.string.button_enroll_finger);
        updateBiometricButton(btnAdminEnrollFace, user.hasFace());
        updateBiometricButton(btnAdminEnrollFinger, user.hasFingerprint());
    }

    private String buildBioSummary(User user) {
        boolean face = user.hasFace();
        boolean finger = user.hasFingerprint();
        if (face && finger) {
            return getString(R.string.bio_summary_both);
        }
        if (face) {
            return getString(R.string.bio_summary_face_only);
        }
        if (finger) {
            return getString(R.string.bio_summary_finger_only);
        }
        return getString(R.string.bio_summary_none);
    }

    private void updateBiometricButton(Button button, boolean enrolled) {
        if (!(button instanceof MaterialButton)) {
            return;
        }
        MaterialButton materialButton = (MaterialButton) button;
        int bgColor = ContextCompat.getColor(this, enrolled ? R.color.bio_ready_bg : R.color.button_tonal_bg);
        int textColor = ContextCompat.getColor(this, enrolled ? R.color.bio_ready_text : R.color.button_tonal_text);
        materialButton.setBackgroundTintList(ColorStateList.valueOf(bgColor));
        materialButton.setTextColor(textColor);
    }

    private void updateChannelMap() {
        if (tvChannel1 == null) {
            return;
        }
        String[] names = new String[6];
        for (User user : cachedUsers) {
            Integer channel = user.getAssignedChannelOrNull();
            if (channel != null && channel >= 1 && channel <= 5) {
                names[channel] = user.getName();
            }
        }
        updateChannelText(tvChannel1, 1, names[1]);
        updateChannelText(tvChannel2, 2, names[2]);
        updateChannelText(tvChannel3, 3, names[3]);
        updateChannelText(tvChannel4, 4, names[4]);
        updateChannelText(tvChannel5, 5, names[5]);
    }

    private void updateChannelText(TextView view, int channel, String name) {
        String label = name == null ? getString(R.string.channel_slot_empty) : name;
        String content = getString(R.string.channel_slot_format, channel, label);
        String text = "● " + content;
        android.text.SpannableString span = new android.text.SpannableString(text);
        int dotColor = ContextCompat.getColor(this, name == null ? R.color.channel_dot_taken : R.color.channel_dot_free);
        span.setSpan(new android.text.style.ForegroundColorSpan(dotColor), 0, 1, android.text.Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
        view.setText(span);
    }

    private void showActionResult(int titleRes, int detailRes) {
        if (cardActionResult == null || tvActionResultTitle == null || tvActionResultDetail == null) {
            return;
        }
        cardActionResult.setVisibility(View.VISIBLE);
        tvActionResultTitle.setText(titleRes);
        tvActionResultDetail.setText(detailRes);
    }

    private void showResultDialog(int titleRes, int detailRes) {
        String message = getString(titleRes) + "\n" + getString(detailRes);
        new MaterialAlertDialogBuilder(this)
                .setTitle(R.string.section_action_result)
                .setMessage(message)
                .setPositiveButton(android.R.string.ok, null)
                .show();
    }

    private void showDeletedDialog() {
        new MaterialAlertDialogBuilder(this)
                .setTitle(R.string.dialog_deleted_title)
                .setMessage(R.string.dialog_deleted_message)
                .setPositiveButton(android.R.string.ok, null)
                .show();
    }

    private void enableDemoMode() {
        demoMode = true;
        cachedUsers.clear();
        User admin = new User(1, "Admin Demo", 1, 2, 1, 1, 1);
        User user = new User(2, "Utilisateur Demo", 2, 1, 0, 0, 1);
        cachedUsers.add(admin);
        cachedUsers.add(user);
        updateUserAdapters();
        selectedBindUser = null;
        currentUser = null;
        selectedDeleteUser = null;
        Toast.makeText(this, getString(R.string.toast_demo_enabled), Toast.LENGTH_SHORT).show();
        showBindStep();
        etSelectUser.requestFocus();
        etSelectUser.post(() -> etSelectUser.showDropDown());
    }

    private void showConnectionStep() {
        screenConnection.setVisibility(View.VISIBLE);
        screenBind.setVisibility(View.GONE);
        screenDashboard.setVisibility(View.GONE);
        tvGreeting.setVisibility(View.GONE);
        stopChannelMapUpdates();
    }

    private void showBindStep() {
        screenConnection.setVisibility(View.GONE);
        screenBind.setVisibility(View.VISIBLE);
        screenDashboard.setVisibility(View.GONE);
        tvGreeting.setVisibility(View.GONE);
        stopChannelMapUpdates();
    }

    private void showDashboardStep() {
        screenConnection.setVisibility(View.GONE);
        screenBind.setVisibility(View.GONE);
        screenDashboard.setVisibility(View.VISIBLE);
        if (currentUser != null) {
            updateDashboardUi(currentUser);
            boolean admin = currentUser.getAuthLevel() == 1;
            if (cardStatus != null) {
                cardStatus.setVisibility(admin ? View.GONE : View.VISIBLE);
            }
            if (cardAdminMenu != null) {
                cardAdminMenu.setVisibility(admin ? View.VISIBLE : View.GONE);
            }
            if (sectionAdminUser != null) {
                sectionAdminUser.setVisibility(View.GONE);
            }
            if (sectionAdminHardware != null) {
                sectionAdminHardware.setVisibility(admin ? View.GONE : View.VISIBLE);
            }
            if (adminUserHeader != null) {
                adminUserHeader.setVisibility(View.GONE);
            }
            if (adminHardwareHeader != null) {
                adminHardwareHeader.setVisibility(View.GONE);
            }
            cardAdminChannels.setVisibility(admin ? View.VISIBLE : View.GONE);
            cardChannelMap.setVisibility(View.VISIBLE);
            cardActions.setVisibility(admin ? View.GONE : View.VISIBLE);
            cardSelfManage.setVisibility(admin ? View.GONE : View.VISIBLE);
            if (ivCafeDashboard != null) {
                ivCafeDashboard.setVisibility(admin ? View.VISIBLE : View.GONE);
            }
            if (admin && selectedAdminUser == null) {
                selectedAdminUser = currentUser;
                updateAdminUi(currentUser);
            }
        }
        if (cardActionResult != null) {
            cardActionResult.setVisibility(View.GONE);
        }
        startChannelMapUpdates();
    }

    private void setLoading(boolean loading) {
        pbLoading.setVisibility(loading ? View.VISIBLE : View.GONE);
        btnLoadUsers.setEnabled(!loading);
        btnBindUser.setEnabled(!loading);
        btnUnlock.setEnabled(!loading);
        btnDeleteUser.setEnabled(!loading);
        btnAdminAssignChannel.setEnabled(!loading);
        btnAdminEnrollFace.setEnabled(!loading);
        btnAdminEnrollFinger.setEnabled(!loading);
        btnAdminDeleteUser.setEnabled(!loading);
        btnAdminUserManagement.setEnabled(!loading);
        btnAdminHardwareControl.setEnabled(!loading);
        btnAdminMenuCreate.setEnabled(!loading);
        btnAdminMenuAssign.setEnabled(!loading);
        btnAdminMenuDelete.setEnabled(!loading);
        btnAdminUserBack.setEnabled(!loading);
        btnAdminHardwareBack.setEnabled(!loading);
        btnUnlock1.setEnabled(!loading);
        btnUnlock2.setEnabled(!loading);
        btnUnlock3.setEnabled(!loading);
        btnUnlock4.setEnabled(!loading);
        btnUnlock5.setEnabled(!loading);
        btnCreateUser.setEnabled(!loading);
        if (!loading) {
            if (currentUser != null) {
                updateDashboardUi(currentUser);
            }
            if (selectedAdminUser != null) {
                updateAdminUi(selectedAdminUser);
            }
        }
    }

    private void showAdminUserSection() {
        if (cardAdminMenu != null) {
            cardAdminMenu.setVisibility(View.GONE);
        }
        if (sectionAdminUser != null) {
            sectionAdminUser.setVisibility(View.VISIBLE);
        }
        if (adminUserHeader != null) {
            adminUserHeader.setVisibility(View.VISIBLE);
        }
        if (sectionAdminHardware != null) {
            sectionAdminHardware.setVisibility(View.GONE);
        }
        if (adminHardwareHeader != null) {
            adminHardwareHeader.setVisibility(View.GONE);
        }
        showAdminUserMenu();
        if (ivCafeDashboard != null) {
            ivCafeDashboard.setVisibility(View.GONE);
        }
        if (cardActionResult != null) {
            cardActionResult.setVisibility(View.GONE);
        }
    }

    private void showAdminHardwareSection() {
        if (cardAdminMenu != null) {
            cardAdminMenu.setVisibility(View.GONE);
        }
        if (sectionAdminHardware != null) {
            sectionAdminHardware.setVisibility(View.VISIBLE);
        }
        if (cardAdminChannels != null) {
            cardAdminChannels.setVisibility(View.VISIBLE);
        }
        if (adminHardwareHeader != null) {
            adminHardwareHeader.setVisibility(View.VISIBLE);
        }
        if (sectionAdminUser != null) {
            sectionAdminUser.setVisibility(View.GONE);
        }
        if (adminUserHeader != null) {
            adminUserHeader.setVisibility(View.GONE);
        }
        if (ivCafeDashboard != null) {
            ivCafeDashboard.setVisibility(View.GONE);
        }
        if (cardActionResult != null) {
            cardActionResult.setVisibility(View.GONE);
        }
    }

    private void showAdminMenu() {
        if (cardAdminMenu != null) {
            cardAdminMenu.setVisibility(View.VISIBLE);
        }
        if (sectionAdminUser != null) {
            sectionAdminUser.setVisibility(View.GONE);
        }
        if (sectionAdminHardware != null) {
            sectionAdminHardware.setVisibility(View.GONE);
        }
        if (adminUserHeader != null) {
            adminUserHeader.setVisibility(View.GONE);
        }
        if (adminHardwareHeader != null) {
            adminHardwareHeader.setVisibility(View.GONE);
        }
        showAdminUserMenu();
        if (ivCafeDashboard != null) {
            ivCafeDashboard.setVisibility(View.VISIBLE);
        }
    }

    private void showAdminUserMenu() {
        if (cardAdminUserMenu != null) {
            cardAdminUserMenu.setVisibility(View.VISIBLE);
        }
        if (sectionAdminAssign != null) {
            sectionAdminAssign.setVisibility(View.GONE);
        }
        if (sectionAdminCreate != null) {
            sectionAdminCreate.setVisibility(View.GONE);
        }
        if (sectionAdminDelete != null) {
            sectionAdminDelete.setVisibility(View.GONE);
        }
    }

    private void showAdminCreateSection() {
        if (cardAdminUserMenu != null) {
            cardAdminUserMenu.setVisibility(View.GONE);
        }
        if (sectionAdminCreate != null) {
            sectionAdminCreate.setVisibility(View.VISIBLE);
        }
        if (sectionAdminAssign != null) {
            sectionAdminAssign.setVisibility(View.GONE);
        }
        if (sectionAdminDelete != null) {
            sectionAdminDelete.setVisibility(View.GONE);
        }
    }

    private void showAdminAssignSection() {
        if (cardAdminUserMenu != null) {
            cardAdminUserMenu.setVisibility(View.GONE);
        }
        if (sectionAdminAssign != null) {
            sectionAdminAssign.setVisibility(View.VISIBLE);
        }
        if (sectionAdminCreate != null) {
            sectionAdminCreate.setVisibility(View.GONE);
        }
        if (sectionAdminDelete != null) {
            sectionAdminDelete.setVisibility(View.GONE);
        }
    }

    private void showAdminDeleteSection() {
        if (cardAdminUserMenu != null) {
            cardAdminUserMenu.setVisibility(View.GONE);
        }
        if (sectionAdminDelete != null) {
            sectionAdminDelete.setVisibility(View.VISIBLE);
        }
        if (sectionAdminAssign != null) {
            sectionAdminAssign.setVisibility(View.GONE);
        }
        if (sectionAdminCreate != null) {
            sectionAdminCreate.setVisibility(View.GONE);
        }
    }

    private void handleAdminUserBack() {
        boolean inSubSection = false;
        if (sectionAdminAssign != null && sectionAdminAssign.getVisibility() == View.VISIBLE) {
            inSubSection = true;
        }
        if (sectionAdminCreate != null && sectionAdminCreate.getVisibility() == View.VISIBLE) {
            inSubSection = true;
        }
        if (sectionAdminDelete != null && sectionAdminDelete.getVisibility() == View.VISIBLE) {
            inSubSection = true;
        }
        if (inSubSection) {
            showAdminUserMenu();
        } else {
            showAdminMenu();
        }
    }

    private void setupDropdown(AutoCompleteTextView view) {
        view.setThreshold(0);
        view.setOnClickListener(v -> view.showDropDown());
        view.setOnFocusChangeListener((v, hasFocus) -> {
            if (hasFocus) {
                view.showDropDown();
            }
        });
    }

    private void showHttpError(int code) {
        Toast.makeText(this, getString(R.string.error_http, code), Toast.LENGTH_SHORT).show();
    }

    private void showNetworkError() {
        Toast.makeText(this, getString(R.string.error_network), Toast.LENGTH_SHORT).show();
    }

    private void startChannelMapUpdates() {
        if (demoMode) {
            updateChannelMap();
        }
        channelMapHandler.removeCallbacks(channelMapRunnable);
        channelMapHandler.postDelayed(channelMapRunnable, CHANNEL_MAP_REFRESH_MS);
    }

    private void stopChannelMapUpdates() {
        channelMapHandler.removeCallbacks(channelMapRunnable);
    }

    private void setupBaseUrlEditing() {
        tilBaseUrl.setEndIconOnClickListener(v -> {
            if (baseUrlEditing) {
                saveBaseUrlFromField();
                setBaseUrlEditable(false);
            } else {
                setBaseUrlEditable(true);
            }
        });

        etBaseUrl.setOnEditorActionListener((v, actionId, event) -> {
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                saveBaseUrlFromField();
                setBaseUrlEditable(false);
                return true;
            }
            return false;
        });

        etBaseUrl.setOnFocusChangeListener((v, hasFocus) -> {
            if (!hasFocus && baseUrlEditing) {
                saveBaseUrlFromField();
                setBaseUrlEditable(false);
            }
        });
    }

    private void saveBaseUrlFromField() {
        String url = normalizeBaseUrlOrEmpty(etBaseUrl.getText().toString().trim());
        saveBaseUrl(url);
        if (url.isEmpty()) {
            Toast.makeText(this, getString(R.string.toast_base_url_cleared), Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(this, getString(R.string.toast_base_url_saved), Toast.LENGTH_SHORT).show();
        }
    }

    private void setBaseUrlEditable(boolean editable) {
        baseUrlEditing = editable;
        etBaseUrl.setFocusable(editable);
        etBaseUrl.setFocusableInTouchMode(editable);
        etBaseUrl.setCursorVisible(editable);
        etBaseUrl.setClickable(editable);
        etBaseUrl.setLongClickable(editable);
        if (editable) {
            etBaseUrl.requestFocus();
            etBaseUrl.setSelection(etBaseUrl.getText() == null ? 0 : etBaseUrl.getText().length());
            InputMethodManager imm = (InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
            if (imm != null) {
                imm.showSoftInput(etBaseUrl, InputMethodManager.SHOW_IMPLICIT);
            }
        } else {
            etBaseUrl.clearFocus();
            InputMethodManager imm = (InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
            if (imm != null) {
                imm.hideSoftInputFromWindow(etBaseUrl.getWindowToken(), 0);
            }
        }
    }

    private void saveBaseUrl(String url) {
        SharedPreferences sp = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        sp.edit().putString(KEY_BASE_URL, url).apply();
    }

    private String loadBaseUrl() {
        SharedPreferences sp = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        return sp.getString(KEY_BASE_URL, "");
    }

    private void saveToken(String token) {
        SharedPreferences sp = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        sp.edit().putString(KEY_TOKEN, token).apply();
    }

    private String loadToken() {
        SharedPreferences sp = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        return sp.getString(KEY_TOKEN, "");
    }

    private void clearToken() {
        SharedPreferences sp = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        sp.edit().remove(KEY_TOKEN).apply();
    }

    private String normalizeBaseUrlOrEmpty(String input) {
        if (input.isEmpty()) return "";
        String url = input;
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "http://" + url;
        }
        // Auto-add port :8000 if user typed an IP without port
        // Logic: if url doesn't end with slash and has no port (e.g. http://192.168.4.1)
        // Heuristic: Check if there is a colon after the protocol part
        int protocolEnd = url.indexOf("://") + 3;
        String addressPart = url.substring(protocolEnd);
        if (!addressPart.contains(":")) {
            if (addressPart.endsWith("/")) {
                url = url.substring(0, url.length() - 1) + ":8000/";
            } else {
                url = url + ":8000/";
            }
        } else {
            if (!url.endsWith("/")) {
                url = url + "/";
            }
        }
        return url;
    }

    private String resolveBaseUrl() {
        String saved = loadBaseUrl();
        if (saved == null || saved.isEmpty()) {
            return normalizeBaseUrlOrEmpty(DEFAULT_IP);
        }
        return saved;
    }

    private ApiService apiForBaseUrl(String baseUrl) {
        prepareNetworkForLocalApi(baseUrl);
        return ApiClient.create(baseUrl);
    }
    
    // ...

    private void bindSelectedUser() {
        if (demoMode) {
            if (selectedBindUser == null) {
                Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
                return;
            }
            currentUser = selectedBindUser;
            showDashboardStep();
            return;
        }
        if (selectedBindUser == null) {
            Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) {
            Toast.makeText(this, getString(R.string.toast_base_url_required), Toast.LENGTH_SHORT).show();
            return;
        }

        String token = UUID.randomUUID().toString();
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.bindDevice(new BindRequest(selectedBindUser.getId(), token)).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (!response.isSuccessful()) {
                    Toast.makeText(MainActivity.this, getString(R.string.toast_bind_failed), Toast.LENGTH_SHORT).show();
                    return;
                }
                saveToken(token);
                currentUser = selectedBindUser;
                Toast.makeText(MainActivity.this, getString(R.string.toast_bind_success), Toast.LENGTH_SHORT).show();
                
                // FORCE transition to dashboard
                new Handler(Looper.getMainLooper()).post(() -> {
                    showDashboardStep();
                    refreshUsers(baseUrl);
                });
            }

            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                Toast.makeText(MainActivity.this, getString(R.string.toast_bind_failed), Toast.LENGTH_SHORT).show();
            }
        });
    }

    // ...

    private void showBindStep() {
        screenConnection.setVisibility(View.GONE);
        screenBind.setVisibility(View.VISIBLE);
        screenDashboard.setVisibility(View.GONE);
        tvGreeting.setVisibility(View.GONE);
        stopChannelMapUpdates();
        if (cardCreateUser != null) {
            cardCreateUser.setVisibility(View.VISIBLE);
        }
    }

    private void showDashboardStep() {
        screenConnection.setVisibility(View.GONE);
        screenBind.setVisibility(View.GONE);
        screenDashboard.setVisibility(View.VISIBLE);
        if (cardCreateUser != null) {
            cardCreateUser.setVisibility(View.GONE);
        }
