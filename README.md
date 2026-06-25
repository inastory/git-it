# gitit (Git-it)

一個極具質感、充滿靈魂的互動式 Git 提交輔助工具 desu Wah! 🐙✨

專為追求 __Conventional Commits 規範__ 與 __極致視覺對齊__ 的開發者設計。再也不用死記 Gitmoji，再也不用擔心漏掉 git push！

## ✨ 核心特色

- **雙核心入口導航 (智能偵測)**：
  - **在 Git 倉庫內**：直接進入工作區掃描與 Commit 流程。
  - **在非 Git 倉庫內**：自動跳出二選一引導，看是要「📥 複製現有專案」還是「✨ 建立全新的 uv Python 專案」。
- **🛠️ 智慧降級與加購機制**：
  - 建立新專案時，若系統沒有安裝 `uv`，會自動問你是否降級用標準的 `git init` 建立乾淨資料夾。
  - 若順利使用 `uv` 初始化專案，還會貼心詢問是否順便一鍵加購虛擬環境（`uv venv`）。
- **🔍 深度穿透偵測 (git status -s -u)**：自動穿透全新建立的資料夾，將裡面所有未追蹤的細部檔案全部揪出來供你勾選，不再只顯示冰冷的資料夾名稱！
- **🎨 完美視覺對齊**：針對 Windows、VS Code 內建終端機（Terminal）環境進行極致優化，動態修正游標渲染，排版絕對對齊不抖動。
- **💡 安全防禦與智慧 Push 引導**：
  - 核心指令全部採用列表格式（List format）傳遞，徹底阻絕 Shell Injection 漏洞。不含任何強行覆蓋或危險 rebase 指令，若發生衝突會主動提示並將主導權交還給使用者。
  - **情況 A (工作區乾淨)**：自動背景比對，若偵測到有漏掉的 Commit，立刻引導你一鍵 Push 同步。
  - **情況 B (工作區有異動)**：流暢地帶你經歷 選檔暂存 ➡️ 選擇 Gitmoji ➡️ 本地 Commit ➡️ 詢問 Push 的一條龍完美閉環。若遠端有新進度導致 Push 被拒絕，會自動跳出提示並引導你安全進行 `git pull` 合併。
- **🗂️ 精準中文對照**：將抽象的 Git 狀態碼（M ,  M, ??, MM）轉譯為優雅易懂的中文標籤。

## 🔑 GitHub Token 認證指南

為了讓工具能夠順利撈出你帳號底下的私有倉庫（Private Repo），需要設定 GitHub 存取憑證。工具具備「智慧多階段環境變數偵測」，您可以根據使用習慣選擇以下兩種放置方式之一：

### 1. 取得您的 GitHub Token
1. 登入 GitHub，點擊右上角頭像 ➡️ **Settings**。
2. 左側選單最下方找到 **Developer Settings** ➡️ **Personal Access Tokens** ➡️ **Tokens (classic)**。
3. 點擊 **Generate new token (classic)**，勾選 **`repo`** 權限，然後生成並複製該 Token。

### 2. 設定環境變數檔案 (.env)
請建立一個名為 `.env` 的檔案，內容格式如下：
```env
GITHUB_USERNAME=您的GitHub帳號名稱
GITHUB_TOKEN=您剛剛複製的ghp_開頭Token金鑰
```

- 方式 A：一勞永逸【全域設定】（最推薦 ⭐️）
    直接將 .env 檔案丟到你電腦的家目錄（Home Directory）底下：

    - Windows：C:\Users\您的使用者名稱\.env

    - Mac / Linux：~/.env
這樣不管你在電腦的哪一個空白資料夾啟動 gitit 準備下載專案，工具都能自動讀到你的通行證！

- 方式 B：因地制宜【專案局部設定】
將 .env 檔案直接放在目前終端機停在底下的那個專案資料夾。如果該資料夾內有 .env，工具會優先讀取它。

## ⚙️ 內建 Gitmoji / 提交規範清單

工具內建以下結構化的對齊規範，讓你的 Git 歷史紀錄像藝術品一樣乾淨：

- __✨ feat__: 新增功能 / 注入新欄位或新模組
- __🐛 fix__: 修正 Bug / 排查解決程式錯誤
- __🛡️ security__: 強化呈送前終極防護盾 / 安全性更新
- __📝 docs__: 修改 README、註解或說明文件
- __🐙 ci__: 本地打包、uv 設定、GitHub Actions 整合
- __🎨 style__: 調整程式碼格式、排版、提示泡泡視覺 (不影響代碼邏輯)
- __🚀 deploy__: 準備發布新版本 / 編譯 EXE 執行檔
- __⚡ perf__: 效能優化 / 提升自動化腳本執行速度
- __♻️ refactor__: 程式碼重構 (不是修改 Bug 也不是新增功能)
- __🔥 remove__: 刪除不再使用的舊程式碼、檔案或功能
- __➕ add_dep__: 新增第三方套件依賴 (例如 uv add xxx)
- __➖ rm_dep__: 移除第三方套件依賴 (例如 uv remove xxx)
- __🔧 config__: 修改設定檔 (如 pyproject.toml / .gitignore / VS Code 設定)
- __🎉 init__: 專案初始化 / 新增全新專案結構或最初始提交

## 🚀 安裝與部署指南

本專案基於新一代超高速 Python 套件管理器 uv 進行管理與全域工具安裝。

### 1. 專案複製與環境初始化
請依序執行以下指令，將專案下載至本地並完成 `uv` 虛擬環境與套件依賴的同步：

```bash
# 1. 複製專案倉庫（請記得將「你的用戶名」替換為實際的 GitHub 帳號）
git clone [https://github.com/你的用戶名/git-it.git](https://github.com/你的用戶名/git-it.git)

# 2. 進入專案目錄
cd git-it

# 3. 建立虛擬環境並自動同步 pyproject.toml 所需的相依套件 (如 inquirer)
uv sync
```

### 2. 生產環境安裝 (全域直接使用)
如果你只是想直接在全域環境使用這款好用的工具，請在專案根目錄下執行：

```bash
uv tool install . --force
```

### 3. 開發者模式安裝 (Editable Mode)
如果你正在對工具進行重構、微調 UI（例如修改 main.py），希望修改後免重新安裝、存檔立刻全域生效測試，請執行：

```bash
uv tool install --editable . --force
```

> 💡 Windows 存取被拒 (os error 5) 防呆小撇步：
> 如果在重新安裝時遇到 Scripts: 存取被拒 錯誤，代表目前的終端機或其他 VS Code 視窗正咬著 gitit.exe。請關閉所有執行過該工具的終端機，或重開 VS Code，即可順利重新安裝！

## 🐙 使用方式

不論你在哪一個 Git 專案目錄下，只要在終端機（VS Code 快捷鍵：Ctrl + `）輕輕敲下：

```bash
gitit
```

隨後工具將自動辨識當前環境：非倉庫環境下會引導你一鍵 Clone 遠端項目或一鍵孵化全新的 uv + Git 專案；倉庫環境下則提供全互動式引導流程，協助您高效且規範化地完成變更暫存、日誌撰寫以及遠端倉庫的同步作業。
> feat: seamlessly stage, commit, and push to GitHub, "git" it done! 🚀