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
    # -s: 簡短模式
    # 💡 重點修正：加上 "-u" 參數，強制 Git 穿透並展開未追蹤資料夾內的所有細部檔案！
    status_output = run_command(["git", "status", "-s", "-u"])
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

def check_unpushed_commits():
    """檢查目前分支是否有尚未推送到遠端（GitHub）的本地提交"""
    try:
        # 1. 取得目前所在的分支名稱（例如 main 或 master）
        branch_output = run_command(["git", "branch", "--show-current"])
        current_branch = branch_output.strip()
        if not current_branch:
            return []

        # 2. 比對遠端追蹤分支與本地分支的差異
        # 例如: origin/main..main
        upstream = f"origin/{current_branch}"
        unpushed_output = run_command(
            ["git", "log", f"{upstream}..{current_branch}", "--oneline"])

        if not unpushed_output or not unpushed_output.strip():
            return []

        # 3. 將未推送的 commit 整理成陣列回傳
        commits = [line.strip() for line in unpushed_output.split("\n") if line.strip()]
        return commits

    except Exception:
        # 如果沒有設定遠端追蹤分支（例如全新的專案），直接當作沒有未推送的
        return []

# -------------------------------------------------------------
# 🧩 步驟積木 (Step Functions)
# -------------------------------------------------------------

def check_and_stage_files(changed_files):
    """【步驟一】引導使用者選擇並暫存 (git add) 檔案"""
    add_question = [
        inquirer.Checkbox(
            'files_to_add',
            message="請選擇要暫存 (git add) 的檔案 [按空白鍵勾選，Enter 送出]",
            choices=changed_files,
            default=[f[1] for f in changed_files]  # 預設全選
        )
    ]

    add_answers = inquirer.prompt(add_question)
    if not add_answers or not add_answers['files_to_add']:
        print("👋 未選擇任何檔案，已取消提交。")
        return False

    selected_files = add_answers['files_to_add']
    print(f"📥 正在暫存 {len(selected_files)} 個檔案...")
    for f in selected_files:
        run_command(["git", "add", f])

    sys.stdout.flush()
    return True

def prompt_commit_message():
    """【步驟二】引導使用者填寫 Gitmoji 與 Commit 訊息"""
    sys.stdout.flush()

    commit_questions = [
        inquirer.List('emoji_pair', message="請選擇這次 Commit 的類型", choices=GITMOJIS),
        inquirer.Text('message', message="請輸入 Commit 訊息", validate=lambda _, x: len(x.strip()) > 0)
    ]

    answers = inquirer.prompt(commit_questions)
    sys.stdout.flush()
    
    if not answers:
        print("👋 已取消 Commit 提交。")
        return None

    return answers

def execute_commit(commit_info):
    """【步驟三】組合訊息並真正執行本地 Commit"""
    selected_emoji = commit_info['emoji_pair']
    user_msg = commit_info['message'].strip()
    final_commit_msg = f"{selected_emoji} {user_msg}"

    print(f"\n📝 即將執行: git commit -m \"{final_commit_msg}\"")
    sys.stdout.flush()

    run_command(["git", "commit", "-m", final_commit_msg])
    print("🎉 本地 Commit 成功完成！\n")
    sys.stdout.flush()

def handle_push_workflow(unpushed_commits=None):
    """【步驟四】處理互動式推送流程 (複用邏輯)"""
    if unpushed_commits:
        print("💡 偵測到本地有尚未推送到 GitHub 的提交：")
        for commit in unpushed_commits:
            print(f"   ✨ {commit}")
        print()

    push_question = [
        inquirer.List(
            'push_action',
            message="是否立刻推送到遠端倉庫 (git push)？",
            choices=[
                ("🚀 好的，立刻同步到 GitHub desu!", "push"),
                ("👋 不用了，先保留在本地電腦就好。", "keep")
            ],
            default="push"
        )
    ]

    push_answer = inquirer.prompt(push_question)

    if push_answer and push_answer['push_action'] == "push":
        print("\n📡 正在推送到 GitHub，請稍候...")
        sys.stdout.flush()

        push_result = run_command(["git", "push"])
        if push_result:
            print(f"\n📦 Git 回傳:\n{push_result}")

        print("\n🚀 雲端同步成功！程式碼已安全送達 GitHub desu Wah! 🐙✨")
    else:
        print("\n👋 已將 Commit 保留在本地倉庫，記得找時間 git push 喔！🐙 WAH!")

# -------------------------------------------------------------
# 🎬 主流程 (Main Orchestrator)
# -------------------------------------------------------------

def main():
    if sys.platform == "win32" and not IS_VSCODE:
        os.system("chcp 65001 > nul")

    print("🐙 [InaStory-Gitmoji] 歡迎使用互動式提交工具 desu Wah! \n")
    sys.stdout.flush()

    # 獲取工作區異動狀態
    changed_files = get_changed_files()

    # -------------------------------------------------------------
    # 情況 A：工作區「很乾淨」，檢查是否有漏掉的 Push
    # -------------------------------------------------------------
    if not changed_files:
        unpushed = check_unpushed_commits()
        if unpushed:
            handle_push_workflow(unpushed_commits=unpushed)
        else:
            print("✅ 目前沒有任何檔案需要提交，且所有進度皆已同步至 GitHub (工作區完美乾淨)！")
        return

    # -------------------------------------------------------------
    # 情況 B：工作區「不乾淨」，按步驟流暢執行
    # -------------------------------------------------------------

    # 1. 處理檔案暫存，如果中途取消則中斷
    if not check_and_stage_files(changed_files):
        return

    # 2. 獲取 Commit 訊息輸入，如果中途取消則中斷
    commit_info = prompt_commit_message()
    if not commit_info:
        return

    # 3. 真正執行 Commit
    execute_commit(commit_info)

    # 4. 詢問是否推送
    handle_push_workflow()

if __name__ == "__main__":
    main()
