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

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "distcapsule_prefs";
    private static final String KEY_BASE_URL = "base_url";
    private static final String KEY_TOKEN = "auth_token";
    private static final String DEFAULT_IP = "192.168.4.1";
    private static final long CHANNEL_MAP_REFRESH_MS = 10000;

    private EditText etBaseUrl;
    private TextInputLayout tilBaseUrl, tilSelectUser;
    private boolean baseUrlEditing = false;

    private Button btnLoadUsers, btnDemo, btnBindUser, btnUnlock, btnDeleteUser;
    private Button btnSelfEnrollFace, btnSelfEnrollFinger;
    private Button btnAdminAssignChannel, btnAdminEnrollFace, btnAdminEnrollFinger, btnAdminDeleteUser;
    private Button btnAdminUserManagement, btnAdminHardwareControl, btnAdminMenuAssign, btnAdminMenuDelete;
    private Button btnUnlock1, btnUnlock2, btnUnlock3, btnUnlock4, btnUnlock5;
    // New Assign Buttons
    private Button[] btnAssigns = new Button[6]; // Index 1-5
    private Integer selectedAssignChannel = null;

    private AutoCompleteTextView etSelectUser, etAdminSelectUser, etAdminDeleteUser;
    private EditText etAdminChannel;

    private TextView tvGreeting, tvBioSummary, tvFaceStatus, tvFingerStatus, tvChannelStatus;
    private TextView tvAdminFaceStatus, tvAdminFingerStatus, tvActionResultTitle, tvActionResultDetail;
    private TextView tvChannel1, tvChannel2, tvChannel3, tvChannel4, tvChannel5, tvSplashTitle;

    private ImageView ivCafeDashboard, ivHeaderCapsule, ivSplashCapsule;
    private View screenConnection, screenBind, screenDashboard, splashOverlay, mainScroll;
    private MaterialCardView cardSelfManage, cardActions, cardStatus, cardAdminChannels, cardChannelMap, cardActionResult;
    private MaterialCardView cardAdminMenu, cardAdminUserMenu;
    private ImageButton btnAdminUserBack, btnAdminHardwareBack;
    private View adminUserHeader, adminHardwareHeader;
    private View sectionAdminUser, sectionAdminHardware, sectionAdminAssign, sectionAdminDelete;
    private ProgressBar pbLoading;

    private final List<User> cachedUsers = new ArrayList<>();
    private final List<User> bindUsers = new ArrayList<>();
    private final List<User> adminUsers = new ArrayList<>();
    private ArrayAdapter<String> bindAdapter;
    private ArrayAdapter<String> adminAdapter;

    private User currentUser;
    private User selectedBindUser;
    private User selectedAdminUser;
    private User selectedDeleteUser;
    private boolean demoMode = false;
    private int debugStep = 0;
    private final Handler channelMapHandler = new Handler(Looper.getMainLooper());

    private final Runnable channelMapRunnable = new Runnable() {
        @Override
        public void run() {
            if (screenDashboard == null || screenDashboard.getVisibility() != View.VISIBLE) return;
            if (demoMode) {
                updateChannelMap();
            } else {
                String baseUrl = resolveBaseUrl();
                if (!baseUrl.isEmpty()) refreshUsers(baseUrl);
            }
            channelMapHandler.postDelayed(this, CHANNEL_MAP_REFRESH_MS);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();
        setupAdapters();
        setupListeners();
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

    private void initViews() {
        etBaseUrl = findViewById(R.id.etBaseUrl);
        tilBaseUrl = findViewById(R.id.tilBaseUrl);
        tilSelectUser = findViewById(R.id.tilSelectUser);
        btnLoadUsers = findViewById(R.id.btnLoadUsers);
        btnDemo = findViewById(R.id.btnDemo);
        btnBindUser = findViewById(R.id.btnBindUser);
        btnUnlock = findViewById(R.id.btnUnlock);
        btnDeleteUser = findViewById(R.id.btnDeleteUser);
        btnSelfEnrollFace = findViewById(R.id.btnSelfEnrollFace);
        btnSelfEnrollFinger = findViewById(R.id.btnSelfEnrollFinger);
        btnAdminAssignChannel = findViewById(R.id.btnAdminAssignChannel);
        btnAdminEnrollFace = findViewById(R.id.btnAdminEnrollFace);
        btnAdminEnrollFinger = findViewById(R.id.btnAdminEnrollFinger);
        btnAdminDeleteUser = findViewById(R.id.btnAdminDeleteUser);
        btnAdminUserManagement = findViewById(R.id.btnAdminUserManagement);
        btnAdminHardwareControl = findViewById(R.id.btnAdminHardwareControl);
        btnAdminMenuAssign = findViewById(R.id.btnAdminMenuAssign);
        btnAdminMenuDelete = findViewById(R.id.btnAdminMenuDelete);
        btnUnlock1 = findViewById(R.id.btnUnlock1);
        btnUnlock2 = findViewById(R.id.btnUnlock2);
        btnUnlock3 = findViewById(R.id.btnUnlock3);
        btnUnlock4 = findViewById(R.id.btnUnlock4);
        btnUnlock5 = findViewById(R.id.btnUnlock5);
        
        btnAssigns[1] = findViewById(R.id.btnAssign1);
        btnAssigns[2] = findViewById(R.id.btnAssign2);
        btnAssigns[3] = findViewById(R.id.btnAssign3);
        btnAssigns[4] = findViewById(R.id.btnAssign4);
        btnAssigns[5] = findViewById(R.id.btnAssign5);
        
        etSelectUser = findViewById(R.id.etSelectUser);
        etAdminSelectUser = findViewById(R.id.etAdminSelectUser);
        etAdminDeleteUser = findViewById(R.id.etAdminDeleteUser);
        etAdminChannel = findViewById(R.id.etAdminChannel);
        tvGreeting = findViewById(R.id.tvGreeting);
        tvBioSummary = findViewById(R.id.tvBioSummary);
        tvFaceStatus = findViewById(R.id.tvFaceStatus);
        tvFingerStatus = findViewById(R.id.tvFingerStatus);
        tvChannelStatus = findViewById(R.id.tvChannelStatus);
        tvAdminFaceStatus = findViewById(R.id.tvAdminFaceStatus);
        tvAdminFingerStatus = findViewById(R.id.tvAdminFingerStatus);
        tvActionResultTitle = findViewById(R.id.tvActionResultTitle);
        tvActionResultDetail = findViewById(R.id.tvActionResultDetail);
        tvChannel1 = findViewById(R.id.tvChannel1);
        tvChannel2 = findViewById(R.id.tvChannel2);
        tvChannel3 = findViewById(R.id.tvChannel3);
        tvChannel4 = findViewById(R.id.tvChannel4);
        tvChannel5 = findViewById(R.id.tvChannel5);
        tvSplashTitle = findViewById(R.id.tvSplashTitle);
        
        ivCafeDashboard = findViewById(R.id.ivCafeDashboard);
        ivHeaderCapsule = findViewById(R.id.ivCapsule);
        ivSplashCapsule = findViewById(R.id.ivSplashCapsule);
        screenConnection = findViewById(R.id.screenConnection);
        screenBind = findViewById(R.id.screenBind);
        screenDashboard = findViewById(R.id.screenDashboard);
        splashOverlay = findViewById(R.id.splashOverlay);
        mainScroll = findViewById(R.id.mainScroll);
        cardSelfManage = findViewById(R.id.cardSelfManage);
        cardActions = findViewById(R.id.cardActions);
        cardStatus = findViewById(R.id.cardStatus);
        cardAdminChannels = findViewById(R.id.cardAdminChannels);
        cardChannelMap = findViewById(R.id.cardChannelMap);
        cardActionResult = findViewById(R.id.cardActionResult);
        cardAdminMenu = findViewById(R.id.cardAdminMenu);
        cardAdminUserMenu = findViewById(R.id.cardAdminUserMenu);
        sectionAdminUser = findViewById(R.id.sectionAdminUser);
        sectionAdminHardware = findViewById(R.id.sectionAdminHardware);
        sectionAdminAssign = findViewById(R.id.sectionAdminAssign);
        sectionAdminDelete = findViewById(R.id.sectionAdminDelete);
        adminUserHeader = findViewById(R.id.adminUserHeader);
        adminHardwareHeader = findViewById(R.id.adminHardwareHeader);
        btnAdminUserBack = findViewById(R.id.btnAdminUserBack);
        btnAdminHardwareBack = findViewById(R.id.btnAdminHardwareBack);
        pbLoading = findViewById(R.id.pbLoading);
    }

    private void setupListeners() {
        btnLoadUsers.setOnClickListener(v -> connectToApi());
        btnBindUser.setOnClickListener(v -> bindSelectedUser());
        btnUnlock.setOnClickListener(v -> unlockChannel());
        btnDeleteUser.setOnClickListener(v -> deleteCurrentUser());
        
        btnSelfEnrollFace.setOnClickListener(v -> {
            if (currentUser != null) triggerEnrollment(currentUser.getId(), true);
        });
        btnSelfEnrollFinger.setOnClickListener(v -> {
            if (currentUser != null) triggerEnrollment(currentUser.getId(), false);
        });

        btnAdminAssignChannel.setOnClickListener(v -> assignAdminChannel());
        btnAdminEnrollFace.setOnClickListener(v -> updateAdminBiometric(true));
        btnAdminEnrollFinger.setOnClickListener(v -> updateAdminBiometric(false));
        btnAdminDeleteUser.setOnClickListener(v -> deleteAdminUser());
        btnAdminUserManagement.setOnClickListener(v -> showAdminUserSection());
        btnAdminHardwareControl.setOnClickListener(v -> showAdminHardwareSection());
        btnAdminMenuAssign.setOnClickListener(v -> showAdminAssignSection());
        btnAdminMenuDelete.setOnClickListener(v -> showAdminDeleteSection());
        
        btnUnlock1.setOnClickListener(v -> unlockSpecificChannel(1));
        btnUnlock2.setOnClickListener(v -> unlockSpecificChannel(2));
        btnUnlock3.setOnClickListener(v -> unlockSpecificChannel(3));
        btnUnlock4.setOnClickListener(v -> unlockSpecificChannel(4));
        btnUnlock5.setOnClickListener(v -> unlockSpecificChannel(5));
        
                        for (int i = 1; i <= 5; i++) {
                            final int ch = i;
                            btnAssigns[i].setOnClickListener(v -> toggleAssignChannel(ch));
                        }
                        
                        btnAdminUserBack.setOnClickListener(v -> handleAdminUserBack());
                        btnAdminHardwareBack.setOnClickListener(v -> showAdminMenu());
                    }

    private void showConnectionStep() {
        screenConnection.setVisibility(View.VISIBLE);
        screenBind.setVisibility(View.GONE);
        screenDashboard.setVisibility(View.GONE);
        stopChannelMapUpdates();
    }

    private void showBindStep() {
        screenConnection.setVisibility(View.GONE);
        screenBind.setVisibility(View.VISIBLE);
        screenDashboard.setVisibility(View.GONE);
        stopChannelMapUpdates();

        // Transform Bind Screen into Registration Screen
        if (etSelectUser != null) {
            etSelectUser.setAdapter(null); // Disable dropdown
            etSelectUser.setText("");
            // IMPORTANT: Restore keyboard for registration name entry
            etSelectUser.setInputType(android.text.InputType.TYPE_CLASS_TEXT);
            etSelectUser.setFocusable(true);
            etSelectUser.setFocusableInTouchMode(true);
            etSelectUser.setCursorVisible(true);
            
            etSelectUser.setHint("Entrez votre nom");
        }
        if (btnBindUser != null) {
            btnBindUser.setText("Créer et se connecter");
            btnBindUser.setOnClickListener(v -> createAndBindUser());
        }
    }

    private void createAndBindUser() {
        String name = etSelectUser.getText().toString().trim();
        if (name.isEmpty()) {
            Toast.makeText(this, "Veuillez entrer un nom", Toast.LENGTH_SHORT).show();
            return;
        }
        
        setLoading(true);
        String baseUrl = resolveBaseUrl();
        ApiService api = apiForBaseUrl(baseUrl);
        
        // Step 1: Create User
        api.createUser(new CreateUserRequest(name, 2, null)).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                if (response.isSuccessful() && response.body() != null) {
                    User newUser = response.body();
                    // Step 2: Bind Device
                    performBind(newUser.getId(), baseUrl);
                } else {
                    setLoading(false);
                    Toast.makeText(MainActivity.this, "Création échouée: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }
            @Override
            public void onFailure(Call<User> call, Throwable t) {
                setLoading(false);
                Toast.makeText(MainActivity.this, "Erreur création: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void performBind(int userId, String baseUrl) {
        String token = UUID.randomUUID().toString();
        apiForBaseUrl(baseUrl).bindDevice(new BindRequest(userId, token)).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (response.isSuccessful()) {
                    saveToken(token);
                    // Fetch full user details to ensure current user object is valid
                    fetchAndEnterDashboard(baseUrl);
                } else {
                    Toast.makeText(MainActivity.this, "Liaison échouée: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }
            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                Toast.makeText(MainActivity.this, "Erreur liaison: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void fetchAndEnterDashboard(String baseUrl) {
        setLoading(true);
        String token = loadToken();
        apiForBaseUrl(baseUrl).auth(new AuthRequest(token)).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                setLoading(false);
                if (response.isSuccessful() && response.body() != null) {
                    currentUser = response.body();
                    showDashboardStep();
                    refreshUsers(baseUrl);
                } else {
                    Toast.makeText(MainActivity.this, "Erreur auth après création", Toast.LENGTH_SHORT).show();
                }
            }
            @Override
            public void onFailure(Call<User> call, Throwable t) {
                setLoading(false);
                Toast.makeText(MainActivity.this, "Erreur réseau après création", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void showDashboardStep() {
        screenConnection.setVisibility(View.GONE);
        screenBind.setVisibility(View.GONE);
        screenDashboard.setVisibility(View.VISIBLE);
        if (currentUser != null) {
            updateDashboardUi(currentUser);
            boolean isAdmin = currentUser.getAuthLevel() == 1;
            if (cardStatus != null) cardStatus.setVisibility(isAdmin ? View.GONE : View.VISIBLE);
            if (cardAdminMenu != null) cardAdminMenu.setVisibility(isAdmin ? View.VISIBLE : View.GONE);
            if (sectionAdminUser != null) sectionAdminUser.setVisibility(View.GONE);
            if (sectionAdminHardware != null) sectionAdminHardware.setVisibility(isAdmin ? View.GONE : View.VISIBLE);
            cardAdminChannels.setVisibility(isAdmin ? View.VISIBLE : View.GONE);
            cardChannelMap.setVisibility(View.VISIBLE);
            cardActions.setVisibility(isAdmin ? View.GONE : View.VISIBLE);
            cardSelfManage.setVisibility(isAdmin ? View.GONE : View.VISIBLE);
            if (ivCafeDashboard != null) ivCafeDashboard.setVisibility(isAdmin ? View.VISIBLE : View.GONE);
            if (isAdmin && selectedAdminUser == null) {
                selectedAdminUser = currentUser;
                updateAdminUi(currentUser);
            }
        }
        if (cardActionResult != null) cardActionResult.setVisibility(View.GONE);
        startChannelMapUpdates();
    }

    private void bindSelectedUser() {
        if (selectedBindUser == null) {
            Toast.makeText(this, getString(R.string.toast_select_user), Toast.LENGTH_SHORT).show();
            return;
        }
        if (demoMode) {
            currentUser = selectedBindUser;
            showDashboardStep();
            return;
        }
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        String token = UUID.randomUUID().toString();
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.bindDevice(new BindRequest(selectedBindUser.getId(), token)).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (response.isSuccessful()) {
                    saveToken(token);
                    currentUser = selectedBindUser;
                    showDashboardStep();
                    refreshUsers(baseUrl);
                } else {
                    Toast.makeText(MainActivity.this, getString(R.string.toast_bind_failed), Toast.LENGTH_SHORT).show();
                }
            }
            @Override
            public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                Toast.makeText(MainActivity.this, getString(R.string.toast_bind_failed), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void connectToApi() {
        if (demoMode) {
            showBindStep();
            return;
        }
        String input = etBaseUrl.getText().toString().trim();
        String normalizedUrl = normalizeBaseUrlOrEmpty(input.isEmpty() ? resolveBaseUrl() : input);
        if (normalizedUrl.isEmpty()) return;

        saveBaseUrl(normalizedUrl);
        ApiService api = apiForBaseUrl(normalizedUrl);
        setLoading(true);
        String token = loadToken();
        if (!token.isEmpty()) {
            api.auth(new AuthRequest(token)).enqueue(new Callback<User>() {
                @Override
                public void onResponse(Call<User> call, Response<User> response) {
                    setLoading(false);
                    if (response.isSuccessful() && response.body() != null) {
                        currentUser = response.body();
                        showDashboardStep();
                        refreshUsers(normalizedUrl);
                    } else {
                        clearToken();
                        loadUsersForBind(normalizedUrl);
                    }
                }
                @Override
                public void onFailure(Call<User> call, Throwable t) {
                    setLoading(false);
                    loadUsersForBind(normalizedUrl);
                }
            });
        } else {
            loadUsersForBind(normalizedUrl);
        }
    }

    private void loadUsersForBind(String baseUrl) {
        ApiService api = apiForBaseUrl(baseUrl);
        setLoading(true);
        api.getUsers().enqueue(new Callback<List<User>>() {
            @Override
            public void onResponse(Call<List<User>> call, Response<List<User>> response) {
                setLoading(false);
                if (response.isSuccessful() && response.body() != null) {
                    cachedUsers.clear();
                    cachedUsers.addAll(response.body());
                    updateUserAdapters();
                    showBindStep();
                } else {
                    // Show error toast
                    String msg = "Error: " + response.code();
                    Toast.makeText(MainActivity.this, msg, Toast.LENGTH_LONG).show();
                }
            }
            @Override
            public void onFailure(Call<List<User>> call, Throwable t) {
                setLoading(false);
                // Show failure toast
                String msg = "Fail: " + t.getMessage();
                Toast.makeText(MainActivity.this, msg, Toast.LENGTH_LONG).show();
            }
        });
    }

    private void refreshUsers(String baseUrl) {
        apiForBaseUrl(baseUrl).getUsers().enqueue(new Callback<List<User>>() {
            @Override
            public void onResponse(Call<List<User>> call, Response<List<User>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    cachedUsers.clear();
                    cachedUsers.addAll(response.body());
                    updateUserAdapters();
                    syncCurrentUserFromCache();
                }
            }
            @Override
            public void onFailure(Call<List<User>> call, Throwable t) {}
        });
    }

    private void setupAdapters() {
        bindAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, new ArrayList<>());
        etSelectUser.setAdapter(bindAdapter);
        setupDropdown(etSelectUser);
        etSelectUser.setOnItemClickListener((p, v, pos, id) -> {
            if (pos >= 0 && pos < bindUsers.size()) selectedBindUser = bindUsers.get(pos);
        });

        adminAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, new ArrayList<>());
        etAdminSelectUser.setAdapter(adminAdapter);
        setupDropdown(etAdminSelectUser);
        etAdminSelectUser.setOnItemClickListener((p, v, pos, id) -> {
            if (pos >= 0 && pos < adminUsers.size()) {
                selectedAdminUser = adminUsers.get(pos);
                updateAdminUi(selectedAdminUser);
            }
        });

        etAdminDeleteUser.setAdapter(adminAdapter);
        setupDropdown(etAdminDeleteUser);
        etAdminDeleteUser.setOnItemClickListener((p, v, pos, id) -> {
            if (pos >= 0 && pos < adminUsers.size()) selectedDeleteUser = adminUsers.get(pos);
        });
    }

    private void updateUserAdapters() {
        bindUsers.clear(); adminUsers.clear();
        List<String> labels = new ArrayList<>();
        for (User user : cachedUsers) {
            String label = user.getId() + " - " + user.getName();
            bindUsers.add(user); adminUsers.add(user);
            labels.add(label);
        }
        bindAdapter.clear(); bindAdapter.addAll(labels); bindAdapter.notifyDataSetChanged();
        adminAdapter.clear(); adminAdapter.addAll(labels); adminAdapter.notifyDataSetChanged();
        updateChannelMap();
    }

    private void syncCurrentUserFromCache() {
        if (currentUser == null) return;
        for (User u : cachedUsers) {
            if (u.getId() == currentUser.getId()) {
                currentUser = u;
                updateDashboardUi(u);
                break;
            }
        }
    }

    private void setLoading(boolean loading) {
        if (pbLoading != null) pbLoading.setVisibility(loading ? View.VISIBLE : View.GONE);
    }

    private void showAdminUserSection() {
        if (cardAdminMenu != null) cardAdminMenu.setVisibility(View.GONE);
        if (sectionAdminUser != null) sectionAdminUser.setVisibility(View.VISIBLE);
        if (adminUserHeader != null) adminUserHeader.setVisibility(View.VISIBLE);
        showAdminUserMenu();
    }

    private void showAdminHardwareSection() {
        if (cardAdminMenu != null) cardAdminMenu.setVisibility(View.GONE);
        if (sectionAdminHardware != null) sectionAdminHardware.setVisibility(View.VISIBLE);
        if (adminHardwareHeader != null) adminHardwareHeader.setVisibility(View.VISIBLE);
    }

    private void showAdminMenu() {
        if (cardAdminMenu != null) cardAdminMenu.setVisibility(View.VISIBLE);
        if (sectionAdminUser != null) sectionAdminUser.setVisibility(View.GONE);
        if (sectionAdminHardware != null) sectionAdminHardware.setVisibility(View.GONE);
        if (adminUserHeader != null) adminUserHeader.setVisibility(View.GONE);
        if (adminHardwareHeader != null) adminHardwareHeader.setVisibility(View.GONE);
    }

    private void showAdminUserMenu() {
        if (cardAdminUserMenu != null) cardAdminUserMenu.setVisibility(View.VISIBLE);
        if (sectionAdminAssign != null) sectionAdminAssign.setVisibility(View.GONE);
        if (sectionAdminDelete != null) sectionAdminDelete.setVisibility(View.GONE);
    }

    private void showAdminAssignSection() {
        if (cardAdminUserMenu != null) cardAdminUserMenu.setVisibility(View.GONE);
        if (sectionAdminAssign != null) sectionAdminAssign.setVisibility(View.VISIBLE);
    }

    private void showAdminDeleteSection() {
        if (cardAdminUserMenu != null) cardAdminUserMenu.setVisibility(View.GONE);
        if (sectionAdminDelete != null) sectionAdminDelete.setVisibility(View.VISIBLE);
    }

    private void handleAdminUserBack() {
        if ((sectionAdminAssign != null && sectionAdminAssign.getVisibility() == View.VISIBLE) ||
            (sectionAdminDelete != null && sectionAdminDelete.getVisibility() == View.VISIBLE)) {
            showAdminUserMenu();
        } else {
            showAdminMenu();
        }
    }

    private void unlockChannel() {
        if (currentUser == null || currentUser.getAssignedChannel() <= 0) return;
        int channel = currentUser.getAssignedChannel();
        if (demoMode) {
            Toast.makeText(this, "Ouverture du canal " + channel, Toast.LENGTH_SHORT).show();
            return;
        }
        String baseUrl = resolveBaseUrl();
        apiForBaseUrl(baseUrl).unlock(channel).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(MainActivity.this, "Ouverture du canal " + channel, Toast.LENGTH_SHORT).show();
                }
            }
            @Override public void onFailure(Call<StatusResponse> call, Throwable t) {}
        });
    }

    private void unlockSpecificChannel(int channel) {
        if (demoMode) {
            Toast.makeText(this, "Ouverture du canal " + channel, Toast.LENGTH_SHORT).show();
            return;
        }
        apiForBaseUrl(resolveBaseUrl()).unlock(channel).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(MainActivity.this, "Ouverture du canal " + channel, Toast.LENGTH_SHORT).show();
                }
            }
            @Override public void onFailure(Call<StatusResponse> call, Throwable t) {}
        });
    }

    private void deleteCurrentUser() {
        if (currentUser == null) return;
        if (demoMode) { currentUser = null; showBindStep(); return; }
        String baseUrl = resolveBaseUrl();
        apiForBaseUrl(baseUrl).deleteUser(currentUser.getId()).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                if (response.isSuccessful()) { currentUser = null; clearToken(); showBindStep(); refreshUsers(baseUrl); }
            }
            @Override public void onFailure(Call<StatusResponse> call, Throwable t) {}
        });
    }

    private void deleteAdminUser() {
        if (selectedDeleteUser == null) return;
        // Store ID locally because selectedDeleteUser might be nulled before response
        int targetId = selectedDeleteUser.getId();
        
        if (demoMode) { 
            cachedUsers.removeIf(u -> u.getId() == targetId); 
            updateUserAdapters(); 
            etAdminDeleteUser.setText("");
            return; 
        }
        
        String baseUrl = resolveBaseUrl();
        apiForBaseUrl(baseUrl).deleteUser(targetId).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(MainActivity.this, "Utilisateur supprimé", Toast.LENGTH_SHORT).show();
                    // 1. Locally remove from cache for instant update
                    cachedUsers.removeIf(u -> u.getId() == targetId);
                    updateUserAdapters(); // Refresh dropdowns
                    
                    // 2. Clear UI
                    etAdminDeleteUser.setText("");
                    etAdminDeleteUser.clearFocus();
                    selectedDeleteUser = null;
                    
                    // 3. Sync from server just in case
                    refreshUsers(baseUrl);
                } else {
                    Toast.makeText(MainActivity.this, "Échec suppression: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }
            @Override public void onFailure(Call<StatusResponse> call, Throwable t) {
                Toast.makeText(MainActivity.this, "Erreur réseau", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void assignAdminChannel() {
        if (selectedAdminUser == null) return;
        Integer channel = selectedAssignChannel;
        
        if (demoMode) { selectedAdminUser.setAssignedChannel(channel); updateAdminUi(selectedAdminUser); return; }
        String baseUrl = resolveBaseUrl();
        
        // Pass 0 to indicate "Release Channel" so JSON is not empty
        Integer apiValue = (channel == null) ? 0 : channel;
        
        apiForBaseUrl(baseUrl).updateUser(selectedAdminUser.getId(), new UpdateUserRequest(null, apiValue)).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                if (response.isSuccessful()) {
                    refreshUsers(baseUrl);
                    if (channel != null) {
                        Toast.makeText(MainActivity.this, selectedAdminUser.getName() + " assigné au Canal " + channel, Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(MainActivity.this, "Canal retiré pour " + selectedAdminUser.getName(), Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(MainActivity.this, "Canal occupé ou erreur: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }
            @Override public void onFailure(Call<User> call, Throwable t) {}
        });
    }
    
    private void toggleAssignChannel(int channel) {
        if (selectedAdminUser == null) return;
        
        // Check if occupied by OTHER user
        for (User u : cachedUsers) {
            if (u.getId() != selectedAdminUser.getId() && u.getAssignedChannel() == channel) {
                Toast.makeText(this, "Canal déjà occupé par " + u.getName(), Toast.LENGTH_SHORT).show();
                return;
            }
        }
        
        if (selectedAssignChannel != null && selectedAssignChannel == channel) {
            selectedAssignChannel = null; // Deselect
        } else {
            selectedAssignChannel = channel;
        }
        updateAssignChannelUi();
        updateAssignButtonText();
    }
    
    private void updateAssignButtonText() {
        if (btnAdminAssignChannel == null) return;
        if (selectedAssignChannel != null) {
            btnAdminAssignChannel.setText("Attribuer Canal " + selectedAssignChannel);
        } else {
            if (selectedAdminUser != null && selectedAdminUser.getAssignedChannel() > 0) {
                btnAdminAssignChannel.setText("Retirer le Canal");
            } else {
                btnAdminAssignChannel.setText("Attribuer");
            }
        }
    }
    
    private void updateAssignChannelUi() {
        if (selectedAdminUser == null) return;
        int currentAssigned = selectedAdminUser.getAssignedChannel();
        
        for (int i = 1; i <= 5; i++) {
            Button btn = btnAssigns[i];
            if (btn == null) continue;
            
            boolean isOccupiedByOther = false;
            for (User u : cachedUsers) {
                if (u.getId() != selectedAdminUser.getId() && u.getAssignedChannel() == i) {
                    isOccupiedByOther = true;
                    break;
                }
            }
            
            btn.setEnabled(true);
            
            // Logic: If it's the pending selection OR (no pending selection AND it's the current channel)
            boolean isHighlight = (selectedAssignChannel != null && selectedAssignChannel == i);
            
            if (isHighlight) {
                // Selected/Current -> Sunflower Yellow
                btn.setBackgroundTintList(ColorStateList.valueOf(0xFFf38942));
                btn.setTextColor(0xFFFFFFFF);
                btn.animate().translationY(-15f).setDuration(200).start();
                btn.setElevation(10f);
            } else if (isOccupiedByOther) {
                // Occupied -> Coral Red
                btn.setBackgroundTintList(ColorStateList.valueOf(0xFFafaeaa));
                btn.setTextColor(0xFFFFFFFF);
                btn.animate().translationY(0f).setDuration(200).start();
                btn.setElevation(0f);
            } else {
                // Free -> Emerald Green
                btn.setBackgroundTintList(ColorStateList.valueOf(0xFFacd07e));
                btn.setTextColor(0xFFFFFFFF);
                btn.animate().translationY(0f).setDuration(200).start();
                btn.setElevation(0f);
            }
        }
    }

    private void updateAdminBiometric(boolean face) {
        if (selectedAdminUser == null) return;
        if (demoMode) { if (face) selectedAdminUser.setHasFace(true); else selectedAdminUser.setHasFingerprint(true); updateAdminUi(selectedAdminUser); return; }
        String baseUrl = resolveBaseUrl();
        ApiService api = apiForBaseUrl(baseUrl);
        Call<StatusResponse> call = face ? api.enrollFace(selectedAdminUser.getId()) : api.enrollFinger(selectedAdminUser.getId());
        call.enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                if (response.isSuccessful()) refreshUsers(baseUrl);
            }
            @Override public void onFailure(Call<StatusResponse> call, Throwable t) {}
        });
    }

    // New helper to avoid duplicate enrollment logic
    private void triggerEnrollment(int userId, boolean isFace) {
        String baseUrl = resolveBaseUrl();
        if (baseUrl.isEmpty()) return;
        setLoading(true);
        ApiService api = apiForBaseUrl(baseUrl);
        Call<StatusResponse> call = isFace ? api.enrollFace(userId) : api.enrollFinger(userId);
        call.enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                setLoading(false);
                if (response.isSuccessful()) {
                    Toast.makeText(MainActivity.this, "Suivez l'écran de la machine", Toast.LENGTH_LONG).show();
                } else {
                    Toast.makeText(MainActivity.this, "Erreur: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }
            @Override public void onFailure(Call<StatusResponse> call, Throwable t) {
                setLoading(false);
                Toast.makeText(MainActivity.this, "Erreur réseau", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void updateDashboardUi(User user) {
        String welcome;
        if (user.getAssignedChannel() > 0) {
            welcome = "Bonjour, " + user.getName() + " !\n\nVotre café est au Canal " + user.getAssignedChannel() + ".";
        } else {
            welcome = "Bonjour, " + user.getName() + " !\nBienvenue chez DistCapsule.";
        }

        // Hide the old greeting view outside the card
        if (tvGreeting != null) tvGreeting.setVisibility(View.GONE);

        // Update the card content
        if (tvBioSummary != null) {
            tvBioSummary.setText(welcome);
            tvBioSummary.setVisibility(View.VISIBLE);
            tvBioSummary.setTextSize(20); // Make it larger and more prominent
        }

        // Hide all old status detail texts inside the card
        if (tvFaceStatus != null) tvFaceStatus.setVisibility(View.GONE);
        if (tvFingerStatus != null) tvFingerStatus.setVisibility(View.GONE);
        if (tvChannelStatus != null) tvChannelStatus.setVisibility(View.GONE);

        // Update Self-Enrollment Buttons
        if (btnSelfEnrollFace != null) {
            if (user.hasFace()) {
                btnSelfEnrollFace.setText("Mettre à jour Face");
                btnSelfEnrollFace.setBackgroundTintList(ColorStateList.valueOf(0xFF8dc842));
                btnSelfEnrollFace.setTextColor(0xFF3F3B3C); // Dark Grey
            } else {
                btnSelfEnrollFace.setText("Ajouter Face");
                btnSelfEnrollFace.setBackgroundTintList(ColorStateList.valueOf(0xFFf4d22e)); // Sunflower Yellow
                btnSelfEnrollFace.setTextColor(0xFF3F3B3C); // Dark Grey
            }
        }
        if (btnSelfEnrollFinger != null) {
            if (user.hasFingerprint()) {
                btnSelfEnrollFinger.setText("Mettre à jour Empreinte");
                btnSelfEnrollFinger.setBackgroundTintList(ColorStateList.valueOf(0xFF8dc842));
                btnSelfEnrollFinger.setTextColor(0xFF3F3B3C); // Dark Grey
            } else {
                btnSelfEnrollFinger.setText("Ajouter Empreinte");
                btnSelfEnrollFinger.setBackgroundTintList(ColorStateList.valueOf(0xFFf4d22e));
                btnSelfEnrollFinger.setTextColor(0xFF3F3B3C); // Dark Grey
            }
        }

        if (btnUnlock != null) {
            btnUnlock.setEnabled(user.getAssignedChannel() > 0);
        }

        updateChannelMap();
    }

    private void updateAdminUi(User user) {
        if (user == null) return;
        
        // Hide text status, use buttons instead
        if (tvAdminFaceStatus != null) tvAdminFaceStatus.setVisibility(View.GONE);
        if (tvAdminFingerStatus != null) tvAdminFingerStatus.setVisibility(View.GONE);
        
        // Face Button Logic
        if (btnAdminEnrollFace != null) {
            if (user.hasFace()) {
                btnAdminEnrollFace.setText("Mettre à jour Face");
                btnAdminEnrollFace.setBackgroundTintList(ColorStateList.valueOf(0xFF8dc842));
                btnAdminEnrollFace.setTextColor(0xFF3F3B3C); // Dark Grey
            } else {
                btnAdminEnrollFace.setText("Ajouter Face");
                btnAdminEnrollFace.setBackgroundTintList(ColorStateList.valueOf(0xFFf4d22e));
                btnAdminEnrollFace.setTextColor(0xFF3F3B3C); // Dark Grey
            }
        }

        // Fingerprint Button Logic
        if (btnAdminEnrollFinger != null) {
            if (user.hasFingerprint()) {
                btnAdminEnrollFinger.setText("Mettre à jour Empreinte");
                btnAdminEnrollFinger.setBackgroundTintList(ColorStateList.valueOf(0xFF8dc842));
                btnAdminEnrollFinger.setTextColor(0xFF3F3B3C); // Dark Grey
            } else {
                btnAdminEnrollFinger.setText("Ajouter Empreinte");
                btnAdminEnrollFinger.setBackgroundTintList(ColorStateList.valueOf(0xFFf4d22e));
                btnAdminEnrollFinger.setTextColor(0xFF3F3B3C); // Dark Grey
            }
        }
        
        // Sync selection state
        selectedAssignChannel = (user.getAssignedChannel() > 0) ? user.getAssignedChannel() : null;
        updateAssignChannelUi();
        updateAssignButtonText();
    }

    private String buildBioSummary(User user) {
        if (user.hasFace() && user.hasFingerprint()) return getString(R.string.bio_summary_both);
        if (user.hasFace()) return getString(R.string.bio_summary_face_only);
        if (user.hasFingerprint()) return getString(R.string.bio_summary_finger_only);
        return getString(R.string.bio_summary_none);
    }

    private void updateChannelMap() {
        String[] names = new String[6];
        for (User u : cachedUsers) {
            int c = u.getAssignedChannel();
            if (c >= 1 && c <= 5) names[c] = u.getName();
        }
        updateChannelText(tvChannel1, 1, names[1]);
        updateChannelText(tvChannel2, 2, names[2]);
        updateChannelText(tvChannel3, 3, names[3]);
        updateChannelText(tvChannel4, 4, names[4]);
        updateChannelText(tvChannel5, 5, names[5]);
    }

    private void updateChannelText(TextView tv, int c, String name) {
        if (tv == null) return;
        tv.setText(String.format("● Canal %d: %s", c, name == null ? "Vide" : name));
        tv.setTextColor(ContextCompat.getColor(this, name == null ? android.R.color.darker_gray : R.color.channel_dot_taken));
    }

    private void showActionResult(int titleRes, int detailRes) {
        String msg = getString(titleRes) + ": " + getString(detailRes);
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
        // Hide the card if it was visible
        if (cardActionResult != null) cardActionResult.setVisibility(View.GONE);
    }

    private void enableDemoMode() {
        demoMode = true;
        cachedUsers.clear();
        cachedUsers.add(new User(1, "Admin Demo", 1, 2, 1, 1, 1));
        cachedUsers.add(new User(2, "User Demo", 2, 1, 0, 0, 1));
        updateUserAdapters();
        showBindStep();
    }

    private void startChannelMapUpdates() {
        channelMapHandler.removeCallbacks(channelMapRunnable);
        channelMapHandler.postDelayed(channelMapRunnable, CHANNEL_MAP_REFRESH_MS);
    }

    private void stopChannelMapUpdates() {
        channelMapHandler.removeCallbacks(channelMapRunnable);
    }

    private String resolveBaseUrl() {
        String saved = loadBaseUrl();
        return saved.isEmpty() ? normalizeBaseUrlOrEmpty(DEFAULT_IP) : saved;
    }

    private ApiService apiForBaseUrl(String baseUrl) {
        prepareNetworkForLocalApi(baseUrl);
        return ApiClient.create(baseUrl);
    }

    private String normalizeBaseUrlOrEmpty(String input) {
        if (input.isEmpty()) return "";
        String url = input;
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "http://" + url;
        }
        
        // Fix: Check for port ONLY in the address part (after protocol)
        // "http://" is 7 chars. 
        int protocolEndIndex = url.indexOf("://") + 3;
        String addressPart = url.substring(protocolEndIndex);
        
        // If address part has no colon (e.g. "192.168.4.1" or "192.168.4.1/"), add port
        if (!addressPart.contains(":")) {
            if (url.endsWith("/")) {
                url = url.substring(0, url.length() - 1) + ":8000/";
            } else {
                url = url + ":8000/";
            }
        }
        
        if (!url.endsWith("/")) {
            url = url + "/";
        }
        return url;
    }

    private void saveBaseUrl(String url) { getSharedPreferences(PREFS_NAME, MODE_PRIVATE).edit().putString(KEY_BASE_URL, url).apply(); }
    private String loadBaseUrl() { return getSharedPreferences(PREFS_NAME, MODE_PRIVATE).getString(KEY_BASE_URL, ""); }
    private void saveToken(String t) { getSharedPreferences(PREFS_NAME, MODE_PRIVATE).edit().putString(KEY_TOKEN, t).apply(); }
    private String loadToken() { return getSharedPreferences(PREFS_NAME, MODE_PRIVATE).getString(KEY_TOKEN, ""); }
    private void clearToken() { getSharedPreferences(PREFS_NAME, MODE_PRIVATE).edit().remove(KEY_TOKEN).apply(); }

    private String stripProtocolAndPort(String url) {
        return url.replace("http://", "").replace("https://", "").replace(":8000", "").replace("/", "");
    }

    private void setupBaseUrlEditing() {
        if (tilBaseUrl != null) tilBaseUrl.setEndIconOnClickListener(v -> setBaseUrlEditable(!baseUrlEditing));
        if (etBaseUrl != null) etBaseUrl.setOnEditorActionListener((v, a, e) -> {
            if (a == EditorInfo.IME_ACTION_DONE) { setBaseUrlEditable(false); return true; }
            return false;
        });
    }

    private void setBaseUrlEditable(boolean e) {
        baseUrlEditing = e;
        if (etBaseUrl == null) return;
        etBaseUrl.setFocusable(e); etBaseUrl.setFocusableInTouchMode(e);
        if (e) {
            etBaseUrl.requestFocus();
            InputMethodManager imm = (InputMethodManager) getSystemService(INPUT_METHOD_SERVICE);
            if (imm != null) imm.showSoftInput(etBaseUrl, InputMethodManager.SHOW_IMPLICIT);
        } else {
            String url = normalizeBaseUrlOrEmpty(etBaseUrl.getText().toString().trim());
            if (!url.isEmpty()) saveBaseUrl(url);
        }
    }

    private void setupDropdown(AutoCompleteTextView v) {
        if (v == null) return;
        // Make it read-only: no keyboard, no manual focus
        v.setInputType(android.text.InputType.TYPE_NULL);
        v.setFocusable(false);
        v.setClickable(true);
        v.setCursorVisible(false);
        
        v.setThreshold(0);
        v.setOnClickListener(view -> v.showDropDown());
        // For some versions of Android, we also need to catch the click on the parent container
        // But for now, simple click should work.
    }

    private void playSplash() {
        if (splashOverlay == null || mainScroll == null || tvSplashTitle == null || ivSplashCapsule == null) {
            return;
        }

        mainScroll.setAlpha(0f);
        mainScroll.setVisibility(View.INVISIBLE);

        tvSplashTitle.setAlpha(0f);
        tvSplashTitle.setScaleX(0.85f);
        tvSplashTitle.setScaleY(0.85f);
        ivSplashCapsule.setAlpha(0f);
        ivSplashCapsule.setTranslationY(-220f);

        ObjectAnimator titleAlpha = ObjectAnimator.ofFloat(tvSplashTitle, View.ALPHA, 0f, 1f);
        ObjectAnimator titleScaleX = ObjectAnimator.ofFloat(tvSplashTitle, View.SCALE_X, 0.85f, 1f);
        ObjectAnimator titleScaleY = ObjectAnimator.ofFloat(tvSplashTitle, View.SCALE_Y, 0.85f, 1f);

        AnimatorSet titleSet = new AnimatorSet();
        titleSet.playTogether(titleAlpha, titleScaleX, titleScaleY);
        titleSet.setDuration(900);

        ObjectAnimator capsuleDrop = ObjectAnimator.ofFloat(
                ivSplashCapsule,
                View.TRANSLATION_Y,
                -220f,
                0f,
                -28f,
                0f,
                -12f,
                0f
        );
        ObjectAnimator capsuleAlpha = ObjectAnimator.ofFloat(ivSplashCapsule, View.ALPHA, 0f, 1f);

        AnimatorSet capsuleSet = new AnimatorSet();
        capsuleSet.playTogether(capsuleDrop, capsuleAlpha);
        capsuleSet.setDuration(1700);
        capsuleSet.setInterpolator(new OvershootInterpolator(0.6f));
        capsuleSet.setStartDelay(150);

        AnimatorSet full = new AnimatorSet();
        full.playSequentially(titleSet, capsuleSet);
        full.addListener(new android.animation.AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(android.animation.Animator animation) {
                splashOverlay.setVisibility(View.GONE);
                mainScroll.setVisibility(View.VISIBLE);
                mainScroll.animate().alpha(1f).setDuration(450).start();
                attemptAutoAuth();
            }
        });
        full.start();
    }

    private void attemptAutoAuth() {
        if (demoMode) {
            return;
        }
        String token = loadToken();
        if (token == null || token.isEmpty()) {
            return;
        }
        connectToApi();
    }

    private void setupDebugScreenToggle() {
        if (ivHeaderCapsule == null) {
            return;
        }
        ivHeaderCapsule.setOnClickListener(v -> {
            debugStep = (debugStep + 1) % 3;
            if (debugStep == 0) {
                showConnectionStep();
            } else if (debugStep == 1) {
                showBindStep();
            } else {
                showDashboardStep();
            }
        });
    }

    private void prepareNetworkForLocalApi(String baseUrl) {
        if (!shouldBindWifi(baseUrl)) {
            return;
        }
        ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        if (cm == null) {
            return;
        }
        Network wifi = findWifiNetwork(cm);
        if (wifi == null) {
            Toast.makeText(this, getString(R.string.toast_connect_wifi), Toast.LENGTH_SHORT).show();
            return;
        }
        boolean bound = cm.bindProcessToNetwork(wifi);
        if (!bound) {
            Toast.makeText(this, getString(R.string.toast_bind_wifi_failed), Toast.LENGTH_SHORT).show();
        }
    }

    @SuppressWarnings("deprecation")
    private Network findWifiNetwork(ConnectivityManager cm) {
        for (Network network : cm.getAllNetworks()) {
            NetworkCapabilities caps = cm.getNetworkCapabilities(network);
            if (caps != null && caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) {
                return network;
            }
        }
        return null;
    }

    private boolean shouldBindWifi(String baseUrl) {
        Uri uri = Uri.parse(baseUrl);
        String host = uri.getHost();
        if (host == null) {
            return false;
        }
        if ("localhost".equalsIgnoreCase(host) || host.endsWith(".local")) {
            return true;
        }
        return isPrivateIpv4(host);
    }

    private boolean isPrivateIpv4(String host) {
        String[] parts = host.split("\\.");
        if (parts.length != 4) {
            return false;
        }
        int[] nums = new int[4];
        for (int i = 0; i < 4; i++) {
            try {
                nums[i] = Integer.parseInt(parts[i]);
            } catch (NumberFormatException e) {
                return false;
            }
            if (nums[i] < 0 || nums[i] > 255) {
                return false;
            }
        }
        if (nums[0] == 10) return true;
        if (nums[0] == 192 && nums[1] == 168) return true;
        if (nums[0] == 172 && nums[1] >= 16 && nums[1] <= 31) return true;
        if (nums[0] == 169 && nums[1] == 254) return true;
        return false;
    }
}
