# git-it (InaStory-Gitmoji)

一個極具質感、充滿靈魂的互動式 Git 提交輔助工具 desu Wah! 🐙✨

專為追求 __Conventional Commits 規範__ 與 __極致視覺對齊__ 的開發者設計。再也不用死記 Gitmoji，再也不用擔心漏掉 git push！

## ✨ 核心特色

- __🔍 深度穿透偵測 (git status -s -u)__：自動穿透全新建立的資料夾，將裡面所有未追蹤的細部檔案全部揪出來供你勾選，不再只顯示冰冷的資料夾名稱！
- __🎨 完美視覺對齊__：針對 Windows、VS Code 內建終端機（Terminal）環境進行極致優化，動態修正游標渲染，排版絕對對齊不抖動。
- __💡 雙軌智慧 Push 引導__：
【次級清單】 __情況 A (工作區乾淨)__：自動背景比對本地與遠端分支，若偵測到有漏掉的 Commit，立刻引導你一鍵 Push 同步。
【次級清單】 __情況 B (工作區有異動)__：流暢地帶你經歷 選檔暂存 ➡️ 選擇 Gitmoji ➡️ 本地 Commit ➡️ 詢問 Push 的一條龍完美閉環。
- __🛠️ 精準中文對照__：將抽象的 Git 狀態碼（M ,  M, ??, MM）轉譯為優雅易懂的中文標籤。

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

隨後工具將自動為您的專案執行互動式引導流程，協助您高效且規範化地完成變更暫存、日誌撰寫以及遠端倉庫的同步作業。 ：
> feat: seamlessly stage, commit, and push to GitHub, "git" it done! 🚀