<p align="center">
  <img src="https://github.com/thjoksi/thj-twitter-token-checker/blob/main/screen.png" alt="logo" width="600"/>
</p>

# 🧪 Twitter Account Checker

A high-performance Twitter account checker using auth_token and ct0, fully multithreaded with live status updates. It supports proxy rotation and categorizes accounts by follower count, tweet count, and account creation date.

---

## 🎥 Setup Video

Watch the step-by-step setup guide here:  
👉 **[Click to watch setup video](https://example.com)**

---

## 📦 Requirements

- Python 3.10 or higher
- Windows OS (for console title updates via `ctypes`)
- Proxy (optional but recommended)

---

## 🐍 Installing Python

1. Download Python from: https://www.python.org/downloads/
2. During installation, check **Add Python to PATH**
3. Confirm installation:
```bash
python --version
```

---

## 🔧 Install Dependencies

```bash
pip install requests colorama rich
```

---

## 📁 Project Structure

```
├── main.py            # Main checker script
├── config.json        # Configuration settings
├── tokens.txt         # List of auth_token:ct0 pairs
├── output/            # Output directory (auto-created)
```

---

## 🧪 tokens.txt Format

Each line must follow this format:

```
username:password:email:ct0:auth_token
```

Example:
```
thj:1234:mail@example.com:ct0value:auth_token_value
```

---

## 🌐 Proxy Setup

To use a proxy, open `config.json` and set the `proxy` value like this:

```json
"proxy": "http://username:password@proxyhost:port"
```

Leave it empty to disable proxy:
```json
"proxy": ""
```

---

## ⚙️ Configuration (`config.json`)

- `thread`: Number of parallel threads
- `followers`: Enable follower-based categorization
- `follower_ranges`: Define custom follower brackets
- `add_followers`: Append follower count to output
- `add_date`: Append account creation year
- `add_tweet`: Append tweet count
- `tweet_count_number`: Min tweet count for `tweet_count.txt`
- `date`: Save by creation year (e.g., `2021.txt`)

---

## 🚀 Running the Bot

```bash
python main.py
```

- Live console HUD shows active processing
- Categorized results saved in `output/` directory

---

## 📂 Output Files

- `suspend.txt`: Suspended or inaccessible accounts
- `blue.txt`: Blue-verified (Gold badge) accounts
- `tweet_count.txt`: High tweet count users
- `1-29.txt`, `10Kplus.txt`, etc.: Follower-based files
- `2020.txt`, `2018.txt`: Year-based files

---

## 👤 Author

- **Made by**: `@thjoksi`
- **Community**: [@fathersoftwitter](https://t.me/fathersoftwitter)
