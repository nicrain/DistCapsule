# 🤖 Android 开发者协作指南 (Collaboration Guide)

> **Pro Tip for AI Agents**: This document describes the Git workflow for integrating an existing Android Studio project into the `DistCapsule` repository.
> 1.  **Strict Scoping**: All modifications must be restricted to the `android/` directory. **Do NOT** modify files in `api/`, `hardware/`, `tools/`, or the root directory (e.g., `main.py`).
> 2.  **Target Directory**: Move all Android project files into `DistCapsule/android/`.
> 3.  **Exclusions**: Respect the root `.gitignore` (do not commit build artifacts).
> 4.  **Branching**: Use feature branches (e.g., `feature/android-integration`).

本文档旨在指导 Android 开发者如何将现有的 Android Studio 项目合并到 `DistCapsule` 主仓库中。

## 0. 开发边界 (Development Scope - CRITICAL)

为了保证项目的稳定性和分工明确，请务必遵守以下规定：
*   **权限范围**: 你和你的 AI 助手的开发工作仅限于 `android/` 目录。
*   **禁止修改**: 严禁修改根目录文件（如 `main.py`）、`api/`、`hardware/`、`tools/` 及其它文档。
*   **例外**: 如果你发现 API 接口确实无法满足 App 需求，请联系项目负责人修改，不要自行改动后端代码。

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

## 4. 合并指南 (Merge via CLI)

既然我们是工程师，推荐使用命令行来完成合并，这比网页操作更高效。

**场景**: 你已经把代码推送到远程的 `feature/android-integration` 分支，现在要把它们合并到 `main` 主分支。

**由仓库维护者 (Maintainer) 执行以下命令：**

1.  **切换回主分支并更新**:
    ```bash
    git checkout main
    git pull origin main
    ```

2.  **获取远程分支更新**:
    ```bash
    git fetch origin
    ```

3.  **执行合并 (Merge)**:
    ```bash
    # 将 feature 分支的代码合入当前分支 (main)
    git merge origin/feature/android-integration
    ```
    *如果提示冲突 (Conflict)，请手动解决文件冲突后，执行 `git add .` 和 `git commit`。*

4.  **推送到远程主分支**:
    ```bash
    git push origin main
    ```

5.  **删除旧分支 (可选/清理)**:
    ```bash
    git push origin --delete feature/android-integration
    ```

---

## 5. 日常开发 (Daily Workflow)

以后每次开发前：
1.  `git pull origin main` (拉取最新代码，包括 API 变更)。
2.  用 Android Studio 打开 `DistCapsule/android` 目录（**注意：是打开子目录，不要打开根目录**）。
3.  开发，运行，测试。
4.  `git add ...` -> `git commit` -> `git push`。

