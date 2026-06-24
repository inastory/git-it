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
    ("✨ feat:       新增功能 / 注入新欄位或新模組", "✨ feat"),
    ("🐛 fix:        修正 Bug / 排查解決程式錯誤", "🐛 fix"),
    ("🛡️ security:    強化呈送前終極防護盾 / 安全性更新", "🛡️ security"),
    ("📝 docs:       修改 README、註解或說明文件", "📝 docs"),
    ("🐙 ci:         本地打包、uv 設定、GitHub Actions 整合", "🐙 ci"),
    ("🎨 style:      調整程式碼格式、排版、提示泡泡視覺 (不影響代碼邏輯)", "🎨 style"),
    ("🚀 deploy:     準備發布新版本 / 編譯 EXE 執行檔", "🚀 deploy"),
    ("⚡ perf:       效能優化 / 提升自動化腳本執行速度", "⚡ perf"),
    ("♻️ refactor:   程式碼重構 (不是修改 Bug 也不是新增功能)", "♻️ refactor"),
    ("🔥 remove:     刪除不再使用的舊程式碼、檔案或功能", "🔥 remove"),
    ("➕ add_dep:    新增第三方套件依賴 (例如 uv add xxx)", "➕ add_dep"),
    ("➖ rm_dep:     移除第三方套件依賴 (例如 uv remove xxx)", "➖ rm_dep"),
    ("🔧 config:     修改設定檔 (如 pyproject.toml / .gitignore)", "🔧 config"),
    ("🎉 chore:      初始化專案 / 建立首個專案起點 Commit", "🎉 chore"),
]

GITMOJIS = []
for display_text, commit_type in RAW_GITMOJIS:
    if IS_VSCODE:
        if "🛡️" in display_text:
            display_text = display_text.replace(
                "🛡️ security:", "🛡️  security:")
        elif "♻️" in display_text:
            display_text = display_text.replace(
                "♻️ refactor:", "♻️  refactor:")
    GITMOJIS.append((display_text, commit_type))

def run_command(cmd):
    """執行系統指令並回傳結果 (支援 UTF-8 保險)"""
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="ignore", check=True
        )
        return result.stdout.rstrip()
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else (
            e.stdout.strip() if e.stdout else "未知錯誤")
        print(f"❌ 執行失敗: {error_msg}")
        sys.exit(1)

def get_changed_files():
    """向 Git 索取目前所有異動、未追蹤的檔案清單"""
    status_output = run_command(["git", "status", "-s", "-u"])
    if not status_output:
        return []

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

        raw_code = line[:2]
        file_path = line[2:].strip().strip('"')
        status_text = STATUS_MAP.get(raw_code, f"{raw_code.strip()} - 異動")
        display_name = f"[{status_text}] {file_path}"
        files.append((display_name, file_path))
    return files

def check_unpushed_commits():
    """檢查目前分支是否有尚未推送到遠端（GitHub）的本地提交"""
    try:
        branch_output = run_command(["git", "branch", "--show-current"])
        current_branch = branch_output.strip()
        if not current_branch:
            return []

        upstream = f"origin/{current_branch}"
        unpushed_output = run_command(
            ["git", "log", f"{upstream}..{current_branch}", "--oneline"])

        if not unpushed_output or not unpushed_output.strip():
            return []

        commits = [line.strip() for line in unpushed_output.split("\n") if line.strip()]
        return commits
    except Exception:
        return []

def is_first_commit():
    """智慧檢查：確保本地與遠端 GitHub 皆完全沒有任何提交歷史"""
    try:
        # 1. 檢查本地是否有任何 commit
        # 如果是一個完全沒 commit 過的乾淨倉庫，這個指令會直接回傳錯誤（因為沒有 HEAD）
        run_command(["git", "rev-parse", "--verify", "HEAD"])

        # 2. 如果能抓到 HEAD，代表本地已經有 commit 了，絕對不是第一次提交
        return False
    except SystemExit:
        # 💡 捕捉 run_command 內部的 sys.exit(1)
        # 當 git rev-parse 失敗時，代表連 HEAD 都沒有，這才是真正的全新專案！
        return True
    except Exception:
        return True

# -------------------------------------------------------------
# 🧩 步驟積木 (Step Functions)
# -------------------------------------------------------------

def check_and_stage_files(changed_files):
    """【步驟一】引導使用者選擇並暫存 (git add) 檔案"""

    # 💡 智慧升級：只要清單裡面「有包含暫存的檔案」，而且「數量大於零」
    has_staged = any("暫存" in f[0] or "新增" in f[0] for f in changed_files)

    if has_staged:
        # 再細分：如果「全部」都是暫存，或者使用者可能想先清空重來
        print("💡 偵測到有檔案已處於暫存狀態（可能來自之前的 soft reset）。")
        reset_question = [
            inquirer.Confirm(
                'should_reset',
                message="是否要先重置 (git reset) 暫存區，以便重新乾淨勾選？",
                default=False  # 設為 False 比較安全，不強迫重置
            )
        ]
        reset_answer = inquirer.prompt(reset_question)
        if reset_answer and reset_answer['should_reset']:
            print("🔄 正在重置暫存區...")
            run_command(["git", "reset"])
            print("❌ 請重新執行 `gitit` 以載入正確的未暫存清單! 🐙")
            return False

    add_question = [
        inquirer.Checkbox(
            'files_to_add',
            message="請選擇要暫存 (git add) 的檔案 [按空白鍵勾選，Enter 送出]",
            choices=changed_files,
            default=[f[1] for f in changed_files]
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

    print()
    sys.stdout.flush()
    return True

def prompt_commit_message():
    """【步驟二】引導使用者填寫 Gitmoji、Scope 與 Commit 訊息"""
    sys.stdout.flush()

    filtered_choices = GITMOJIS

    # 💡 智慧動態選單：如果是第一次提交，只顯示 init 選項
    if is_first_commit():
        # 只過濾出帶有 "🎉 chore" 的那個選項
        filtered_choices = [item for item in GITMOJIS if "🎉 chore" in item[1]]
        print("🎉 偵測到這是此專案的首次提交 (First Commit)！已自動為您鎖定初始化選項。")

    # 2.1 選擇 Gitmoji 類型
    type_questions = [
        inquirer.List('emoji_pair', message="請選擇這次 Commit 的類型", choices=filtered_choices)
    ]
    sys.stdout.flush()

    type_answers = inquirer.prompt(type_questions)
    sys.stdout.flush()
    if not type_answers:
        print("👋 已取消 Commit 提交。")
        return None

    base_type = type_answers['emoji_pair']

    # 2.2 填寫影響範圍 Scope (如果是首次提交，預設填好 "init")
    default_scope = "init" if is_first_commit() else ""
    scope_questions = [
        inquirer.Text(
            'scope',
            message=f"請輸入影響範圍 Scope [目前預設: {default_scope if default_scope else '無'}]",
            default=default_scope
        )
    ]
    scope_answers = inquirer.prompt(scope_questions)
    sys.stdout.flush()
    if scope_answers is None:
        print("👋 已取消 Commit 提交。")
        return None

    user_scope = scope_answers['scope'].strip()

    # 2.3 輸入 Commit 主訊息 (如果是首次提交，預設提示 "first commit")
    default_msg = "first commit" if is_first_commit() else ""
    msg_questions = [
        inquirer.Text(
            'message',
            message="請輸入 Commit 訊息",
            default=default_msg,
            validate=lambda _, x: len(x.strip()) > 0
        )
    ]
    msg_answers = inquirer.prompt(msg_questions)
    sys.stdout.flush()
    if not msg_answers:
        print("👋 已取消 Commit 提交。")
        return None

    user_msg = msg_answers['message'].strip()

    # 2.4 智慧型拼接 Conventional Commits 格式
    if user_scope:
        final_commit_msg = f"{base_type}({user_scope}): {user_msg}"
    else:
        final_commit_msg = f"{base_type}: {user_msg}"

    return {"final_msg": final_commit_msg}


def execute_commit(commit_info):
    """【步驟三】組合訊息並真正執行本地 Commit"""
    final_commit_msg = commit_info['final_msg']

    print(f"\n📝 即將執行: git commit -m \"{final_commit_msg}\"")
    sys.stdout.flush()

    run_command(["git", "commit", "-m", final_commit_msg])
    print("🎉 本地 Commit 成功完成！\n")
    sys.stdout.flush()

def handle_push_workflow(unpushed_commits=None):
    """【步驟四】處理互動式推送流程"""
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

    changed_files = get_changed_files()

    if not changed_files:
        unpushed = check_unpushed_commits()
        if unpushed:
            handle_push_workflow(unpushed_commits=unpushed)
        else:
            print("✅ 目前沒有任何檔案需要提交，且所有進度皆已同步至 GitHub (工作區完美乾淨)！")
        return

    if not check_and_stage_files(changed_files):
        return

    commit_info = prompt_commit_message()
    if not commit_info:
        return

    execute_commit(commit_info)
    handle_push_workflow()


if __name__ == "__main__":
    main()
