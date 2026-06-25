import sys
import os
import subprocess
import inquirer
import json
import urllib.request
import urllib.error

def fetch_github_repos(username):
    """透過 GitHub API 動態抓取倉庫，並精準識別 Token 是否過期或無效"""
    token = os.environ.get("GITHUB_TOKEN")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Gitit-CLI-Tool)',
        'Accept': 'application/vnd.github.v3+json'
    }

    if token:
        print("🔑 偵測到環境變數中的 GITHUB_TOKEN，將啟用私有倉庫讀取權限...")
        url = "https://api.github.com/user/repos?per_page=100&sort=updated"
        headers['Authorization'] = f"token {token}"
    else:
        print("🌐 未偵測到 Token，將以匿名公開模式讀取...")
        url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"

    req = urllib.request.Request(url, headers=headers)

    try:
        print(f"📡 正在從 GitHub 索取專案清單...")
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                repos_data = json.loads(response.read().decode('utf-8'))

                repo_choices = []
                for repo in repos_data:
                    is_private = "🔒 " if repo.get('private') else "📦 "
                    display = f"{is_private}{repo['name']} - {repo['description'] or '無描述'}"
                    repo_choices.append(
                        (display, (repo['name'], repo['clone_url'])))

                return repo_choices

    except urllib.error.HTTPError as e:
        # 🎯 這裡就是精準識別 Token 過期的關鍵防線！
        if e.code == 401:
            print("\n❌ 認證失敗：您的 GITHUB_TOKEN 可能已過期、被撤銷或不正確！")
            print(
                "💡 請至 GitHub (Settings -> Developer Settings) 重新產生 Token 並更新您的 .env 檔案。")
            # 彈性處理：Token 壞掉時，自動降級為「免 Token 匿名模式」重新抓取公開專案
            if token:
                print("\n🔄 正在嘗試自動降級為【匿名公開模式】繼續執行...\n")
                os.environ.pop("GITHUB_TOKEN", None)  # 拔除壞掉的 Token
                return fetch_github_repos(username)   # 重新呼叫自己
        elif e.code == 404:
            print(f"\n❌ 找不到該 GitHub 帳號: '{username}'，請檢查拼字是否正確。")
        else:
            print(f"\n❌ GitHub API 回傳錯誤 (HTTP {e.code}): {e.reason}")
        return []

    except Exception as e:
        print(f"❌ 無法連線至 GitHub API (請檢查網路連線): {e}")
        return []

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

# 1. 偵測環境
IS_VSCODE = os.environ.get("TERM_PROGRAM") == "vscode"

def load_env():
    """載入【目前工作目錄】或【使用者家目錄】下的 .env，若缺少關鍵變數則噴出單行指引"""
    cwd_env = os.path.join(os.getcwd(), ".env")
    home_dir = os.path.expanduser("~")
    home_env = os.path.join(home_dir, ".env")

    # 1. 優先權分流導航
    target_env = cwd_env if os.path.exists(cwd_env) else (
        home_env if os.path.exists(home_env) else None)

    # 2. 解析檔案並寫入環境變數
    if target_env:
        with open(target_env, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")

    # 3. 🎯 檢查關鍵變數，若遺漏則印出極簡的單行提示 (One-line troubleshooting)
    missing = [v for v in ["GITHUB_USERNAME", "GITHUB_TOKEN"] if not os.environ.get(v)]
    if missing:
        print(
            f"⚠️ 缺少環境變數 {missing}：請至家目錄建立 '{os.path.join(home_dir, '.env')}' 並寫入 KEY=VALUE 格式。")

# 2. 定義視覺對齊的 Gitmoji 清單
RAW_GITMOJIS = [
    ("✨ feat:       新增功能 / 注入新欄位或新模組", "✨ feat"),
    ("🐛 fix:        修正 Bug / 排查解決程式錯誤", "🐛 fix"),
    ("♻️ refactor:   程式碼重構 (不是修改 Bug 也不是新增功能)", "♻️ refactor"),
    ("📝 docs:       修改 README、註解或說明文件", "📝 docs"),
    ("🎨 style:      調整程式碼格式、排版、提示泡泡視覺 (不影響代碼邏輯)", "🎨 style"),
    ("⚡ perf:       效能優化 / 提升自動化腳本執行速度", "⚡ perf"),
    ("🔧 config:     修改設定檔 (如 pyproject.toml / cliff.toml)", "🔧 config"),
    ("⚙️ chore:      日常維護 / 調整 .gitignore、調整本機開發腳本", "⚙️ chore"),
    ("🐙 ci:         本地打包、uv 設定、GitHub Actions 整合", "🐙 ci"),
    ("🚀 deploy:     準備發布新版本 / 編譯 EXE 執行檔", "🚀 deploy"),
    ("🔥 remove:     刪除不再使用的舊程式碼、檔案或功能", "🔥 remove"),
    ("➕ add_dep:    新增第三方套件依賴 (例如 uv add xxx)", "➕ add_dep"),
    ("➖ rm_dep:     移除第三方套件依賴 (例如 uv remove xxx)", "➖ rm_dep"),
    ("🛡️ security:   強化呈送前終極防護盾 / 安全性更新", "🛡️ security"),
    ("◀️ revert:     版本回滾 / 撤銷先前的 Commit 提交紀錄", "◀️ revert"),
    ("🎉 init:       初始化專案 / 建立首個專案起點 Commit", "🎉 init"),
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

def is_git_repository():
    """安全檢查目前目錄是否為 Git 倉庫"""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.returncode == 0

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

def create_new_uv_project():
    """【全新功能】引導建立專案：支援 uv 自動建立、無 uv 降級純 git、以及智慧選配 .venv"""
    sys.stdout.flush()

    # 1. 詢問專案名稱
    name_question = [
        inquirer.Text('project_name', message="請輸入新專案的名稱 (例如: my-awesome-app)", validate=lambda _, x: len(x.strip()) > 0)
    ]
    name_answer = inquirer.prompt(name_question)
    if not name_answer:
        print("👋 已取消操作。")
        return

    project_name = name_answer['project_name'].strip()

    # 2. 安全檢查：確保目前資料夾下沒有同名專案
    if os.path.exists(project_name):
        print(f"⚠️ 警告: 目前路徑下已存在名為「{project_name}」的檔案或資料夾！")
        return

    print(f"\n🚀 正在建立新專案: {project_name}...")
    sys.stdout.flush()

    try:
        # 3. 嘗試使用 uv 初始化專案（此步驟在新版 uv 中會一併自動處理 git init 與 .gitignore）
        subprocess.run(["uv", "init", project_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ 成功透過 uv 初始化專案與 Git 倉庫。")

        # 4. 🎯 既然有 uv，詢問是否要順便建立虛擬環境 .venv？
        venv_question = [
            inquirer.Confirm(
                'create_venv', message="是否順便為此專案建立虛擬環境 (.venv)？", default=True)
        ]
        venv_answer = inquirer.prompt(venv_question)

        if venv_answer and venv_answer['create_venv']:
            print("📦 正在建立虛擬環境 (uv venv)...")
            sys.stdout.flush()
            # 在建立好的專案資料夾內執行 uv venv
            subprocess.run(["uv", "venv"], cwd=project_name, check=True)
            print("✅ 虛擬環境 .venv 建立成功！")

        # 5. 提示使用者完工與手動 cd 指引
        print(f"\n🎉 專案 {project_name} 建立成功！")
        print(
            f"💡 接下來請手動輸入：\n   👉 cd {project_name}\n   👉 uv run main.py (若有建立 venv)")
        print("🐙 WAH!")

    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        # 🎯 核心防呆：捕捉到找不到 uv 或 uv 執行失敗，觸發降級問答！
        print("\n⚠️ 系統找不到 'uv' 指令或 uv 執行失敗！")
        sys.stdout.flush()

        fallback_question = [
            inquirer.Confirm(
                'fallback_git', message="是否降級改用標準的 'git init' 來為您建立並初始化一個乾淨的 Git 資料夾？", default=True)
        ]
        fallback_answer = inquirer.prompt(fallback_question)

        if fallback_answer and fallback_answer['fallback_git']:
            try:
                print(f"📁 正在建立基本資料夾: {project_name}/")
                os.makedirs(project_name, exist_ok=True)

                print("🗂️ 正在初始化本地 Git 倉庫 (git init)...")
                subprocess.run(["git", "init"], cwd=project_name, check=True)

                print(f"\n🎉 乾淨的 Git 專案 {project_name} 建立成功！")
                print(f"💡 接下來請手動輸入：\n   👉 cd {project_name}")
            except Exception as git_err:
                print(f"❌ 建立失敗，發生預期之外的錯誤: {git_err}")
        else:
            print("👋 已取消操作，未建立任何專案。")

def handle_non_repo_workflow():
    """【新功能 1 升級版】非倉庫環境下，提供 Clone 與 Create 兩大互動流分流"""
    sys.stdout.flush()

    # 0. 顯示引導大選單
    action_question = [
        inquirer.List(
            'init_action',
            message="偵測到目前非 Git 倉庫！請選擇您想執行的操作：",
            choices=[
                ("📥 複製現有的 GitHub 遠端專案 (Clone)", "clone"),
                ("✨ 建立全新的 uv Python 專案 (Create New)", "create")
            ],
            default="clone"
        )
    ]
    action_answer = inquirer.prompt(action_question)
    if not action_answer:
        print("👋 已取消操作。")
        return

    # 🌟 核心分流邏輯
    if action_answer['init_action'] == "create":
        # 走新寫好的 uv 新增專案流
        create_new_uv_project()
        return

    # ----- 以下為原本的 Clone 專案流程 -----
    username = os.environ.get("GITHUB_USERNAME")

    if not username:
        user_questions = [
            inquirer.Text('username', message="請輸入 GitHub 使用者帳號", validate=lambda _, x: len(x.strip()) > 0)
        ]
        user_answers = inquirer.prompt(user_questions)
        if not user_answers:
            print("👋 已取消操作。")
            return
        username = user_answers['username'].strip()
    else:
        print(f"👤 已從設定自動識別 GitHub 帳號: {username}")

    repo_choices = fetch_github_repos(username)
    if not repo_choices:
        print("👋 未找到任何可讀取的倉庫，程式結束。")
        return

    repo_questions = [
        inquirer.List('selected_repo', message=f"請選擇要下載的專案？", choices=repo_choices)
    ]
    repo_answers = inquirer.prompt(repo_questions)
    if not repo_answers:
        print("👋 已取消操作。")
        return

    repo_name, clone_url = repo_answers['selected_repo']

    print(f"\n📂 正在檢查資料夾是否存在...")
    if os.path.exists(repo_name):
        print(f"⚠️ 警告: 目前路徑下已存在名為「{repo_name}」的檔案或資料夾！")
        print("👋 為避免覆蓋，請先手動變更或移除該資料夾後再試。")
        return

    print(f"📁 正在建立專案資料夾: {repo_name}/")
    os.makedirs(repo_name, exist_ok=True)

    print(f"🚀 正在將遠端倉庫下載至該資料夾內...")
    sys.stdout.flush()

    try:
        subprocess.run(["git", "clone", clone_url, "."], cwd=repo_name, check=True)
        print(f"\n🎉 專案 {repo_name} 下載成功！")
        print(f"💡 您現在可以 cd {repo_name} 開始開發了 desu Wah! 🐙✨")
    except subprocess.CalledProcessError:
        print(f"❌ 專案下載失敗，請檢查網路連線或專案權限。")

# -------------------------------------------------------------
# 🎬 主流程 (Main Orchestrator)
# -------------------------------------------------------------

def main():
    load_env()

    if sys.platform == "win32" and not IS_VSCODE:
        os.system("chcp 65001 > nul")

    print("🐙 [InaStory-Gitmoji] 歡迎使用互動式提交工具 desu Wah! \n")
    sys.stdout.flush()

    # 🚀 檢查目前是否為 Git 倉庫
    if not is_git_repository():
        print("🔍 偵測到目前目錄「不是」Git 倉庫...")
        handle_non_repo_workflow()
        return

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
