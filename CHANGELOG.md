## [unreleased]

### 🚀 Features

- Initial commit
- Add "git add" function
- Add function to ask user to push to github
- Check for unpushed commits when working tree is clean
- **core**: add optional interactive scope support for conventional commits
- **core**: add first commit detection
- **init**: add interactive menu to clone with user account(.env) or create new uv project
- **git**: add safe pull prompt on push rejection and handle failure

### 🐛 Bug Fixes

- Update subprocess codec
- Truncated status code spaces and added Chinese alignment
- Terminal redraw loop and ghosting in prompt selection on Windows
- Untracked files inside new folders not listing in file selection
- **pyproject**: gitit not read as package
- **core**: run_command strip the first space

### ♻️ Refactor

- Rename project and folder to git-it.
- Modularize main function and reuse push workflow
- **naming**: unify project and package name to gitit
- **cli**: align RAW_GITMOJIS options with git-cliff parsers

### 📝 Documentation

- **todo**: create todo<span>.md</span> for tracking upcoming features
- **readme**: include guild to init a project and get the github token

### 🎨 Styling

- Change y/n to list option when ask for push

### 🔧 Configuration

- Hide python cache and egg-info from vscode explorer
- README<span>.md</span> usage workflow
- **readme**: add guild add guide to clone and setup the project
- **package**: setup hatchling as build backend
- **changelog**: create cliff.toml and generate changelog<span>.md</span>
