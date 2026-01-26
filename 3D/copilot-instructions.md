# GitHub Copilot Instructions for "Base_Distributeur" Project

## 1. 核心交互协议 (Core Protocol)
*   **先询问，后执行 (Ask Before Action)**: 禁止在未获得用户明确“同意”的情况下直接修改代码文件。
*   **流程 (Workflow)**:
    1.  **分析 (Analyze)**: 理解用户需求，检查现有代码。
    2.  **提案 (Propose)**: 用自然语言描述修改计划，解释思路。
    3.  **等待 (Wait)**: 等待用户回复“同意”或提出修改意见。
    4.  **执行 (Execute)**: 使用工具修改代码。
*   **语言 (Language)**: 始终使用中文 (zh-cn) 回复。

## 2. 项目背景 (Project Context)
*   **项目名称**: Nespresso 胶囊分发器 (Amazon Replica)。
*   **Python 环境**: `/Users/z31wang/Documents/MIASHS/.venv`
*   **技术栈**: Python + `solid2` 库 (OpenSCAD wrapper)。
*   **核心文件**: `Base_Distributeur.py` -> 生成 `Base_Distributeur.scad`。

## 3. 设计规范 (Design Specifications)
*   **坐标系定义**:
    *   **左 (Left)**: 正 X 轴 (+X), 对应变量 `leg_l`。
    *   **右 (Right)**: 负 X 轴 (-X), 对应变量 `leg_r`。
    *   **前 (Front)**: 负 Y 轴 (-Y)。
    *   **上 (Up)**: 正 Z 轴 (+Z)。
*   **关键尺寸**:
    *   总宽: 260.0 mm
    *   总高: 310.0 mm
    *   倾角: 15.0 度 (向后倾斜)
*   **特殊构造**:
    *   **全局地面切割 (Global Ground Cut)**: 在 `__main__` 中旋转后执行，确保底座平整 (Z=0)。
    *   **滑轨槽 (Grooves)**: 在 `__main__` 中旋转后水平切割，确保平行于地面。
    *   **侧边孔 (Sidecar Holes)**: 位于右腿 (`leg_r`)，包含垂直列和水平排。

## 4. 代码风格 (Code Style)
*   **精度控制**: 涉及角度或复杂坐标计算时，结果保留 2 位小数 (`round(x, 2)`)，避免 SCAD 文件过大。
*   **渲染优化**: 圆形部件 (`cylinder`) 必须指定 `_fn=64` (大孔) 或 `_fn=32` (小孔) 以保证平滑度。
*   **布尔运算**: 尽量使用 `union()` 集合同一类切除体，然后一次性 `difference()`，减少 CSG 树深度。
