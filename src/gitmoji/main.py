import os
import subprocess
import sys
import inquirer

# 1. 偵測環境
IS_VSCODE = os.environ.get("TERM_PROGRAM") == "vscode"

# 2. 定義基礎的 Gitmoji 清單
RAW_GITMOJIS = [
    ("✨ feat:       新增功能 / 注入新欄位或新模組", "✨"),
    ("🐛 fix:        修正 Bug / 排查解決程式錯誤", "🐛"),
    ("🛡️ security:   強化呈送前終極防護盾 / 安全性更新", "🛡️"),
    ("📝 docs:       修改 README、註解或說明文件", "📝"),
    ("🐙 ci:         本地打包、uv 設定、GitHub Actions 整合", "🐙"),
    ("🎨 style:      調整程式碼格式、排版、提示泡泡視覺 (不影響代碼邏輯)", "🎨"),
    ("🚀 deploy:     準備發布新版本 / 編譯 EXE 執行檔", "🚀"),
    ("⚡ perf:       效能優化 / 提升自動化腳本執行速度", "⚡"),
    ("♻️ refactor:   程式碼重構 (不是修改 Bug 也不是新增功能)", "♻️"),
    ("🔥 remove:     刪除不再使用的舊程式碼、檔案或功能", "🔥"),
    ("➕ add_dep:    新增第三方套件依賴 (例如 uv add xxx)", "➕"),
    ("➖ rm_dep:     移除第三方套件依賴 (例如 uv remove xxx)", "➖"),
    ("🔧 config:     修改設定檔 (如 pyproject.toml / .gitignore)", "🔧"),
]

# 3. 如果在 VS Code，因為渲染不同，我們動態對 🛡️ 和 ♻️ 的前置空格進行「抽離」或「補償」
GITMOJIS = []
for display_text, icon in RAW_GITMOJIS:
    # 💡 經過反覆測試：
    # 如果是在 VS Code 內，🛡️ 和 ♻️ 的視覺寬度會少一格，所以我們多補一個空格把它們推過去
    if IS_VSCODE:
        if "🛡️" in display_text:
            display_text = display_text.replace(
                "🛡️ security:", "🛡️  security:")
        elif "♻️" in display_text:
            display_text = display_text.replace(
                "♻️ refactor:", "♻️  refactor:")

    GITMOJIS.append((display_text, icon))

def run_command(cmd):
    """執行系統指令並回傳結果"""
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr.strip() else e.stdout.strip()
        print(f"❌ 執行失敗: {error_msg}")
        sys.exit(1)

def main():
    if sys.platform == "win32" and not IS_VSCODE:
        os.system("chcp 65001 > nul")

    print("🐙 [InaStory-Gitmoji] 開始建立 Commit desu Wah! \n")

    # 4. 讓使用者用鍵盤上下鍵選擇 Emoji
    questions = [
        inquirer.List(
            'emoji_pair',
            message="請選擇這次 Commit 的類型",
            choices=GITMOJIS,
        ),
        inquirer.Text(
            'message',
            message="請輸入 Commit 訊息 (例如: 支援自動預測中文通告檔名)",
            validate=lambda _, x: len(x.strip()) > 0
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        print("👋 已取消提交。")
        return

    # 5. 組合最終的 Commit 訊息
    selected_emoji = answers['emoji_pair']
    user_msg = answers['message'].strip()

    final_commit_msg = f"{selected_emoji} {user_msg}"

    print(f"\n📝 即將執行的指令: git commit -m \"{final_commit_msg}\"")

    # 6. 呼叫 Git 執行提交
    run_command(["git", "commit", "-m", final_commit_msg])
    print("\n🎉 Commit 成功完成！🐙 WAH!")

if __name__ == "__main__":
    main()
