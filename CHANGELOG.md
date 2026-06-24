## [unreleased]

### ♻️ Refactor

- Rename project and folder to git-it.
- Modularize main function and reuse push workflow
- **naming**: unify project and package name to gitit

### 🎨 Styling

- Change y/n to list option when ask for push

### 🐛 Bug Fixes

- Update subprocess codec
- Truncated status code spaces and added Chinese alignment
- Terminal redraw loop and ghosting in prompt selection on Windows
- Untracked files inside new folders not listing in file selection
- **pyproject**: gitit not read as package
- **core**: run_command strip the first space

### 📝 Documentation

- **todo**: create todo<span>.md</span> for tracking upcoming features

### 🔧 Configuration

- Hide python cache and egg-info from vscode explorer
- README<span>.md</span> usage workflow
- **readme**: add guild add guide to clone and setup the project
- **package**: setup hatchling as build backend

### 🚀 Features

- Initial commit
- Add "git add" function
- Add function to ask user to push to github
- Check for unpushed commits when working tree is clean
- **core**: add optional interactive scope support for conventional commits
- **core**: add first commit detection
