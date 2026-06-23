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

    # 💡 完美的「符號 + 中文對照表」：刻意補齊空格讓格式絕對對齊！
    STATUS_MAP = {
        "M ": "M  - 暫存",  # 已暫存
        " M": " M - 修改",  # 未暫存修改
        "MM": "MM - 雙改",  # 雙重修改
        "A ": "A  - 新增",  # 已暫存的新檔案
        "??": "?? - 新檔",  # 未追蹤新檔案
        "D ": "D  - 刪除",  # 已暫存的刪除
        " D": " D - 刪除",  # 未暫存的刪除
        "R ": "R  - 改名",  # 重新命名
    }

    files = []
    for line in status_output.split("\n"):
        if not line.strip():
            continue

        # 1. 精準擷取前兩個字元的原始狀態碼（不先 strip 才能比對空格）
        raw_code = line[:2]

        # 2. 擷取後面的檔案路徑並移除可能存在的引號
        file_path = line[2:].strip().strip('"')

        # 3. 根據對照表轉換成中文，如果遇到冷門符號則保留原始去空格的代碼
        status_text = STATUS_MAP.get(raw_code, f"{raw_code.strip()} - 異動")

        # 4. 組合極具質感的顯示文字：[M  - 修改] pyproject.toml
        display_name = f"[{status_text}] {file_path}"

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
    print("🎉 本地 Commit 成功完成！")
    sys.stdout.flush()

    # 🚀 步驟四：互動式詢問是否立刻 Push 到 GitHub
    push_question = [
        inquirer.List(
            'push_action',
                message="是否立刻推送到遠端倉庫 (git push)？",
                choices=[
                    ("🚀 好的，立刻同步到 GitHub desu!", "push"),
                    ("👋 不用了，先保留在本地電腦就好。", "keep")
                ],
            default="push"  # 預設停在第一個選項
        )
    ]

    push_answer = inquirer.prompt(push_question)

    if push_answer and push_answer['push_action'] == "push":
        print("\n📡 正在推送到 GitHub，請稍候...")
        sys.stdout.flush()

        # 執行 git push
        push_result = run_command(["git", "push"])

        # 把 Git 的成功推送訊息印出來讓使用者安心
        if push_result:
            print(f"\n📦 Git 回傳:\n{push_result}")

        print("\n🚀 雲端同步成功！程式碼已安全送達 GitHub desu Wah! 🐙✨")
    else:
        print("\n👋 已將 Commit 保留在本地倉庫，記得找時間 git push 喔！🐙 WAH!")

if __name__ == "__main__":
    main()