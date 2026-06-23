import sys
import os
import subprocess
import inquirer

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

# 1. 偵測環境
IS_VSCODE = os.environ.get("TERM_PROGRAM") == "vscode"

# 2. 定義視覺對齊的 Gitmoji 清單
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

GITMOJIS = []
for display_text, icon in RAW_GITMOJIS:
    if IS_VSCODE:
        if "🛡️" in display_text:
            display_text = display_text.replace(
                "🛡️ security:", "🛡️  security:")
        elif "♻️" in display_text:
            display_text = display_text.replace(
                "♻️ refactor:", "♻️  refactor:")
    GITMOJIS.append((display_text, icon))


def run_command(cmd):
    """執行系統指令並回傳結果 (支援 UTF-8 保險)"""
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="ignore", check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else (
            e.stdout.strip() if e.stdout else "未知錯誤")
        print(f"❌ 執行失敗: {error_msg}")
        sys.exit(1)


def get_changed_files():
    """向 Git 索取目前所有異動、未追蹤的檔案清單"""
    # -s: 簡短模式, --porcelain: 適合腳本解析的穩定格式
    status_output = run_command(["git", "status", "-s"])
    if not status_output:
        return []

    files = []
    for line in status_output.split("\n"):
        if not line.strip():
            continue
        # Git status 輸出的前兩個字元是狀態碼（例如 M , ?? ），後面是檔名
        status_code = line[:2].strip()
        file_path = line[2:].strip().strip('"')  # 移除可能存在的引號

        # 組合美觀的顯示文字：[狀態] 檔案路徑
        display_name = f"[{status_code}] {file_path}"
        files.append((display_name, file_path))
    return files


def main():
    if sys.platform == "win32" and not IS_VSCODE:
        os.system("chcp 65001 > nul")

    print("🐙 [InaStory-Gitmoji] 歡迎使用互動式提交工具 desu Wah! \n")
    sys.stdout.flush()

    # 🟢 步驟一：檢查並選擇要 git add 的檔案
    changed_files = get_changed_files()
    if not changed_files:
        print("✅ 目前沒有任何檔案需要提交 (Git 工作區很乾淨)！")
        return

    # 建立第一個問題：多選清單 (Checkbox)
    add_question = [
        inquirer.Checkbox(
            'files_to_add',
            message="請選擇要暫存 (git add) 的檔案 [按空白鍵勾選，Enter 送出]",
            choices=changed_files,
            default=[f[1] for f in changed_files]  # 預設幫你全選，省時間！
        )
    ]

    add_answers = inquirer.prompt(add_question)
    if not add_answers or not add_answers['files_to_add']:
        print("👋 未選擇任何檔案，已取消提交。")
        return

    # 執行選中檔案的 git add
    selected_files = add_answers['files_to_add']
    print(f"📥 正在暫存 {len(selected_files)} 個檔案...")
    for f in selected_files:
        run_command(["git", "add", f])

    sys.stdout.flush()

    # 🔵 步驟二：選擇 Emoji 與輸入 Commit 訊息
    commit_questions = [
        inquirer.List(
            'emoji_pair',
            message="請選擇這次 Commit 的類型",
            choices=GITMOJIS,
        ),
        inquirer.Text(
            'message',
            message="請輸入 Commit 訊息",
            validate=lambda _, x: len(x.strip()) > 0
        )
    ]

    commit_answers = inquirer.prompt(commit_questions)
    if not commit_answers:
        print("👋 已取消 Commit 提交。")
        return

    # 🟤 步驟三：組合並執行 Commit
    selected_emoji = commit_answers['emoji_pair']
    user_msg = commit_answers['message'].strip()
    final_commit_msg = f"{selected_emoji} {user_msg}"

    print(f"\n📝 即將執行: git commit -m \"{final_commit_msg}\"")
    sys.stdout.flush()

    run_command(["git", "commit", "-m", final_commit_msg])
    print("\n🎉 檔案暫存與 Commit 成功完成！🐙 WAH!")


if __name__ == "__main__":
    main()