# 🤖 Android 开发者协作指南 (Collaboration Guide)

本文档旨在指导 Android 开发者如何将现有的 Android Studio 项目合并到 `DistCapsule` 主仓库中。

## 1. 准备工作 (Preparation)

1.  **备份**: 请先把你现有的 Android 项目备份一份（打个包放一边），以防操作失误。
2.  **获取仓库**:
    打开终端 (Terminal) 或 Git Bash，克隆主仓库：
    ```bash
    git clone https://github.com/nicrain/DistCapsule.git
    cd DistCapsule
    ```

## 2. 代码迁移 (Migration)

你需要把你现有的 Android 项目文件移动到 `DistCapsule/android/` 目录下。

**正确的文件结构应该是这样的：**
```text
DistCapsule/ (根目录)
├── api/
├── hardware/
├── android/          <-- 你的领地
│   ├── app/          <-- 你的 app 模块
│   ├── gradle/
│   ├── build.gradle
│   ├── settings.gradle
│   └── ...
├── .gitignore        <-- 根目录的忽略文件 (已配置好 Android 规则)
└── README.md
```

**操作步骤：**
1.  打开你的 Android 项目文件夹。
2.  **全选**里面的所有文件（app, gradle, build.gradle 等）。
3.  **剪切/复制**。
4.  **粘贴**到 `DistCapsule/android/` 文件夹中。

## 3. 提交代码 (Commit & Push)

在 `DistCapsule` 根目录下执行：

1.  **创建分支** (推荐):
    ```bash
    git checkout -b feature/android-integration
    ```

2.  **检查状态**:
    ```bash
    git status
    ```
    *你应该看到 `android/app/...` 等一堆文件变红了。*
    *如果你看到 `android/build/` 或 `.gradle` 文件，请**不要提交**，联系负责人检查 `.gitignore`。*

3.  **提交更改**:
    ```bash
    git add android/
    git commit -m "feat(android): import initial android studio project"
    ```

4.  **推送到远程**:
    ```bash
    git push origin feature/android-integration
    ```

## 4. 合并 (Merge)

1.  打开 GitHub 仓库页面。
2.  你会看到 "Compare & pull request" 的提示。
3.  点击它，创建一个 **Pull Request (PR)**。
4.  通知负责人 (Nicrain) 进行 Review 和 Merge。

---

## 5. 日常开发 (Daily Workflow)

以后每次开发前：
1.  `git pull origin main` (拉取最新代码，包括 API 变更)。
2.  用 Android Studio 打开 `DistCapsule/android` 目录（**注意：是打开子目录，不要打开根目录**）。
3.  开发，运行，测试。
4.  `git add ...` -> `git commit` -> `git push`。
