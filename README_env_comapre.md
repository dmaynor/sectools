# 🚀 Shell Environment Tracker & Comparator

`compare_env.sh` is a tool that:
✅ **Captures environment variables, functions, and hooks before sourcing a file**  
✅ **Sources the specified file in a chosen shell (`zsh`, `bash`, `fish`, etc.)**  
✅ **Re-captures the environment after sourcing**  
✅ **Compares the two states and displays differences or persistent values**  
✅ **Can log results to an SQLite database for historical tracking**  

---

## 🛠 Installation

Clone the repository and make the script executable:

```bash
git clone https://github.com/yourusername/dotfiles_public.git
cd dotfiles_public
chmod +x compare_env.sh
```

---

## 🚀 Usage

```bash
./compare_env.sh -s SHELL -f FILE [OPTIONS]
```

### ✅ Basic Examples

#### 1️⃣ Compare Environment Changes in Zsh

```bash
./compare_env.sh -s zsh -f ~/.zshrc --added --removed --persisted
```

✅ **Shows added, removed, and persistent environment variables, functions, and hooks.**

#### 2️⃣ See Only Added Variables in Bash

```bash
./compare_env.sh -s bash -f ~/.bashrc --added
```

✅ **Displays only newly added variables.**

#### 3️⃣ Enable Logging and Track Changes Over Time

```bash
./compare_env.sh -s zsh -f ~/.zshrc --enable-logging
```

✅ **Creates an SQLite database (`~/.env_compare/env_history.db`) and logs results automatically.**

#### 4️⃣ View Past Logged Changes

```bash
sqlite3 ~/.env_compare/env_history.db "SELECT * FROM env_history ORDER BY timestamp DESC LIMIT 10;"
```

✅ **Retrieve previous snapshots of your environment variables.**

---

## ⚙ CLI Options

| **Option** | **Description** |
|------------|----------------|
| `-s SHELL` | Specify the shell (`zsh`, `bash`, `fish`) to use for sourcing. |
| `-f FILE` | Specify the file to source. |
| `--added` | Show newly added environment variables/functions/hooks. |
| `--removed` | Show removed environment variables/functions/hooks. |
| `--persisted` | Show unchanged environment variables/functions/hooks. |
| `--enable-logging` | Create an SQLite database (`~/.env_compare/env_history.db`) and log results. |

---

## 🚀 Setting Up Automatic Logging

You can **automate logging via cron** to track environment changes over time.

### 1️⃣ Add a Cron Job

To log changes every hour, add this to your crontab (`crontab -e`):

```bash
0 * * * * /path/to/compare_env.sh -s zsh -f ~/.zshrc --enable-logging
```

✅ **This will track environment changes every hour and save them to the database.**

---

## 🔥 Future Enhancements

- **A separate CLI tool for analyzing historical changes**
- **Webhooks for remote logging**
- **Integration with system monitoring tools**

🚀 **Now you can track every environment change over time! Feel free to contribute improvements!** 🔥
