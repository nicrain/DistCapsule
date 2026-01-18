package net.chezxinqi.distcapsule;

import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
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
    private TextInputLayout tilBaseUrl;
    private boolean baseUrlEditing = false;

    private Button btnLoadUsers, btnDemo, btnBindUser, btnUnlock, btnDeleteUser;
    private Button btnAdminAssignChannel, btnAdminEnrollFace, btnAdminEnrollFinger, btnAdminDeleteUser;
    private Button btnAdminUserManagement, btnAdminHardwareControl, btnAdminMenuCreate, btnAdminMenuAssign, btnAdminMenuDelete;
    private Button btnUnlock1, btnUnlock2, btnUnlock3, btnUnlock4, btnUnlock5;
    // New Assign Buttons
    private Button[] btnAssigns = new Button[6]; // Index 1-5
    private Integer selectedAssignChannel = null;
    private Button btnCreateUser;

    private AutoCompleteTextView etSelectUser, etAdminSelectUser, etAdminDeleteUser;
    private EditText etCreateName, etCreateAuthLevel, etCreateChannel, etAdminChannel;

    private TextView tvGreeting, tvBioSummary, tvFaceStatus, tvFingerStatus, tvChannelStatus;
    private TextView tvAdminFaceStatus, tvAdminFingerStatus, tvActionResultTitle, tvActionResultDetail;
    private TextView tvChannel1, tvChannel2, tvChannel3, tvChannel4, tvChannel5;

    private ImageView ivCafeDashboard;
    private View screenConnection, screenBind, screenDashboard, splashOverlay;
    private MaterialCardView cardSelfManage, cardActions, cardStatus, cardAdminChannels, cardChannelMap, cardCreateUser, cardActionResult;
    private MaterialCardView cardAdminMenu, cardAdminUserMenu;
    private ImageButton btnAdminUserBack, btnAdminHardwareBack;
    private View adminUserHeader, adminHardwareHeader;
    private View sectionAdminUser, sectionAdminHardware, sectionAdminAssign, sectionAdminCreate, sectionAdminDelete;
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
        etBaseUrl.setText(savedUrl.isEmpty() ? DEFAULT_IP : stripProtocolAndPort(savedUrl));
        setBaseUrlEditable(false);

        showConnectionStep();
        playSplash();
    }

    private void initViews() {
        etBaseUrl = findViewById(R.id.etBaseUrl);
        tilBaseUrl = findViewById(R.id.tilBaseUrl);
        btnLoadUsers = findViewById(R.id.btnLoadUsers);
        btnDemo = findViewById(R.id.btnDemo);
        btnBindUser = findViewById(R.id.btnBindUser);
        btnUnlock = findViewById(R.id.btnUnlock);
        btnDeleteUser = findViewById(R.id.btnDeleteUser);
        btnAdminAssignChannel = findViewById(R.id.btnAdminAssignChannel);
        btnAdminEnrollFace = findViewById(R.id.btnAdminEnrollFace);
        btnAdminEnrollFinger = findViewById(R.id.btnAdminEnrollFinger);
        btnAdminDeleteUser = findViewById(R.id.btnAdminDeleteUser);
        btnAdminUserManagement = findViewById(R.id.btnAdminUserManagement);
        btnAdminHardwareControl = findViewById(R.id.btnAdminHardwareControl);
        btnAdminMenuCreate = findViewById(R.id.btnAdminMenuCreate);
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
        
        btnCreateUser = findViewById(R.id.btnCreateUser);
        etSelectUser = findViewById(R.id.etSelectUser);
        etAdminSelectUser = findViewById(R.id.etAdminSelectUser);
        etAdminDeleteUser = findViewById(R.id.etAdminDeleteUser);
        etCreateName = findViewById(R.id.etCreateName);
        etCreateAuthLevel = findViewById(R.id.etCreateAuthLevel);
        etCreateChannel = findViewById(R.id.etCreateChannel);
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
        ivCafeDashboard = findViewById(R.id.ivCafeDashboard);
        screenConnection = findViewById(R.id.screenConnection);
        screenBind = findViewById(R.id.screenBind);
        screenDashboard = findViewById(R.id.screenDashboard);
        splashOverlay = findViewById(R.id.splashOverlay);
        cardSelfManage = findViewById(R.id.cardSelfManage);
        cardActions = findViewById(R.id.cardActions);
        cardStatus = findViewById(R.id.cardStatus);
        cardAdminChannels = findViewById(R.id.cardAdminChannels);
        cardChannelMap = findViewById(R.id.cardChannelMap);
        cardCreateUser = findViewById(R.id.cardCreateUser);
        cardActionResult = findViewById(R.id.cardActionResult);
        cardAdminMenu = findViewById(R.id.cardAdminMenu);
        cardAdminUserMenu = findViewById(R.id.cardAdminUserMenu);
        sectionAdminUser = findViewById(R.id.sectionAdminUser);
        sectionAdminHardware = findViewById(R.id.sectionAdminHardware);
        sectionAdminAssign = findViewById(R.id.sectionAdminAssign);
        sectionAdminCreate = findViewById(R.id.sectionAdminCreate);
        sectionAdminDelete = findViewById(R.id.sectionAdminDelete);
        adminUserHeader = findViewById(R.id.adminUserHeader);
        adminHardwareHeader = findViewById(R.id.adminHardwareHeader);
        btnAdminUserBack = findViewById(R.id.btnAdminUserBack);
        btnAdminHardwareBack = findViewById(R.id.btnAdminHardwareBack);
        pbLoading = findViewById(R.id.pbLoading);
    }

    private void setupListeners() {
        btnLoadUsers.setOnClickListener(v -> connectToApi());
        btnDemo.setOnClickListener(v -> enableDemoMode());
        btnBindUser.setOnClickListener(v -> bindSelectedUser());
        btnUnlock.setOnClickListener(v -> unlockChannel());
        btnDeleteUser.setOnClickListener(v -> deleteCurrentUser());
        btnAdminAssignChannel.setOnClickListener(v -> assignAdminChannel());
        btnAdminEnrollFace.setOnClickListener(v -> updateAdminBiometric(true));
        btnAdminEnrollFinger.setOnClickListener(v -> updateAdminBiometric(false));
        btnAdminDeleteUser.setOnClickListener(v -> deleteAdminUser());
        btnAdminUserManagement.setOnClickListener(v -> showAdminUserSection());
        btnAdminHardwareControl.setOnClickListener(v -> showAdminHardwareSection());
        btnAdminMenuCreate.setOnClickListener(v -> showAdminCreateSection());
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
        
        btnCreateUser.setOnClickListener(v -> createUser());
        btnAdminUserBack.setOnClickListener(v -> handleAdminUserBack());
        btnAdminHardwareBack.setOnClickListener(v -> showAdminMenu());
    }

    private void playSplash() {
        if (splashOverlay != null) {
            splashOverlay.setVisibility(View.VISIBLE);
            new Handler(Looper.getMainLooper()).postDelayed(() -> splashOverlay.setVisibility(View.GONE), 2000);
        }
    }

    private void prepareNetworkForLocalApi(String baseUrl) {
        // Implementation for network preparation if needed
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
        if (cardCreateUser != null) cardCreateUser.setVisibility(View.GONE); // Ensure admin card is hidden
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
        if (cardCreateUser != null) cardCreateUser.setVisibility(View.GONE);
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
        if (sectionAdminCreate != null) sectionAdminCreate.setVisibility(View.GONE);
        if (sectionAdminDelete != null) sectionAdminDelete.setVisibility(View.GONE);
    }

    private void showAdminCreateSection() {
        if (cardAdminUserMenu != null) cardAdminUserMenu.setVisibility(View.GONE);
        if (sectionAdminCreate != null) sectionAdminCreate.setVisibility(View.VISIBLE);
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
            (sectionAdminCreate != null && sectionAdminCreate.getVisibility() == View.VISIBLE) ||
            (sectionAdminDelete != null && sectionAdminDelete.getVisibility() == View.VISIBLE)) {
            showAdminUserMenu();
        } else {
            showAdminMenu();
        }
    }

    private void unlockChannel() {
        if (currentUser == null || currentUser.getAssignedChannel() <= 0) return;
        if (demoMode) {
            showActionResult(R.string.action_unlock_title, R.string.action_unlock_detail);
            return;
        }
        String baseUrl = resolveBaseUrl();
        apiForBaseUrl(baseUrl).unlock(currentUser.getAssignedChannel()).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                if (response.isSuccessful()) showActionResult(R.string.action_unlock_title, R.string.action_unlock_detail);
            }
            @Override public void onFailure(Call<StatusResponse> call, Throwable t) {}
        });
    }

    private void unlockSpecificChannel(int channel) {
        if (demoMode) {
            showActionResult(R.string.action_unlock_title, R.string.action_unlock_detail);
            return;
        }
        apiForBaseUrl(resolveBaseUrl()).unlock(channel).enqueue(new Callback<StatusResponse>() {
            @Override
            public void onResponse(Call<StatusResponse> call, Response<StatusResponse> response) {
                if (response.isSuccessful()) showActionResult(R.string.action_unlock_title, R.string.action_unlock_detail);
            }
            @Override public void onFailure(Call<StatusResponse> call, Throwable t) {}
        });
    }

    private void createUser() {
        String name = etCreateName.getText().toString().trim();
        if (name.isEmpty()) return;
        String authText = etCreateAuthLevel.getText().toString().trim();
        int authLevel = authText.equals("1") ? 1 : 2;
        String chanText = etCreateChannel.getText().toString().trim();
        Integer channel = chanText.isEmpty() ? null : Integer.parseInt(chanText);

        if (demoMode) {
            cachedUsers.add(new User(cachedUsers.size() + 1, name, authLevel, channel, 0, 0, 1));
            updateUserAdapters();
            return;
        }
        String baseUrl = resolveBaseUrl();
        apiForBaseUrl(baseUrl).createUser(new CreateUserRequest(name, authLevel, channel)).enqueue(new Callback<User>() {
            @Override
            public void onResponse(Call<User> call, Response<User> response) {
                if (response.isSuccessful()) refreshUsers(baseUrl);
            }
            @Override public void onFailure(Call<User> call, Throwable t) {}
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
                // Selected/Current -> Orange + Pop Up
                btn.setBackgroundTintList(ColorStateList.valueOf(0xFFFF8F00)); // Amber
                btn.setTextColor(0xFF000000);
                btn.animate().translationY(-15f).setDuration(200).start(); // Pop up effect
                btn.setElevation(10f); // Add shadow
            } else if (isOccupiedByOther) {
                // Occupied -> Red
                btn.setBackgroundTintList(ColorStateList.valueOf(0xFFC62828)); // Red
                btn.setTextColor(0xFFFFFFFF);
                btn.animate().translationY(0f).setDuration(200).start();
                btn.setElevation(0f);
            } else {
                // Free -> Green
                btn.setBackgroundTintList(ColorStateList.valueOf(0xFF4CAF50)); // Green
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

    private void updateDashboardUi(User user) {
        if (tvGreeting != null) tvGreeting.setText("Bonjour, " + user.getName());
        if (tvBioSummary != null) tvBioSummary.setText(buildBioSummary(user));
        if (tvFaceStatus != null) tvFaceStatus.setText(user.hasFace() ? R.string.bio_face_ready : R.string.bio_face_pending);
        if (tvFingerStatus != null) tvFingerStatus.setText(user.hasFingerprint() ? R.string.bio_finger_ready : R.string.bio_finger_pending);
        if (tvChannelStatus != null) tvChannelStatus.setText(user.getAssignedChannel() > 0 ? "Canal " + user.getAssignedChannel() : "Aucun canal");
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
                btnAdminEnrollFace.setBackgroundTintList(ColorStateList.valueOf(0xFF2E7D32)); // Dark Green
                btnAdminEnrollFace.setTextColor(0xFFFFFFFF);
            } else {
                btnAdminEnrollFace.setText("Ajouter Face");
                btnAdminEnrollFace.setBackgroundTintList(ColorStateList.valueOf(0xFFFF8F00)); // Orange
                btnAdminEnrollFace.setTextColor(0xFF000000);
            }
        }

        // Fingerprint Button Logic
        if (btnAdminEnrollFinger != null) {
            if (user.hasFingerprint()) {
                btnAdminEnrollFinger.setText("Mettre à jour Empreinte");
                btnAdminEnrollFinger.setBackgroundTintList(ColorStateList.valueOf(0xFF2E7D32)); // Dark Green
                btnAdminEnrollFinger.setTextColor(0xFFFFFFFF);
            } else {
                btnAdminEnrollFinger.setText("Ajouter Empreinte");
                btnAdminEnrollFinger.setBackgroundTintList(ColorStateList.valueOf(0xFFFF8F00)); // Orange
                btnAdminEnrollFinger.setTextColor(0xFF000000);
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
        if (cardActionResult != null) {
            cardActionResult.setVisibility(View.VISIBLE);
            if (tvActionResultTitle != null) tvActionResultTitle.setText(titleRes);
            if (tvActionResultDetail != null) tvActionResultDetail.setText(detailRes);
        }
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
}
