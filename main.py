import random
import time
import requests
import json
import os
import ctypes
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from colorama import init
from rich.console import Console, Group
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from rich.text import Text

init(autoreset=True)

print_lock = Lock()
console_rich = Console()
log_entries = []


def get_header_panel() -> Align:
    art = '''
  _   _      _   _        _                     _               _             
 | |_| |__  (_) | |_ ___ | | _____ _ __     ___| |__   ___  ___| | _____ _ __ 
 | __| '_ \ | | | __/ _ \| |/ / _ \ '_ \   / __| '_ \ / _ \/ __| |/ / _ \ '__|
 | |_| | | || | | || (_) |   <  __/ | | | | (__| | | |  __/ (__|   <  __/ |   
  \__|_| |_|/ |  \__\___/|_|\_\___|_| |_|  \___|_| |_|\___|\___|_|\_\___|_|   
          |__/                                                                
              made by @thjoksi   |   community: @fathersoftwitter
'''
    return Align.center(Panel.fit(art, border_style="cyan", padding=(1, 2)))


def render() -> Panel:
    return Panel(Group(get_header_panel(), *log_entries[-100:]), border_style="bright_blue")


def console_log(text: str, live: Live | None = None, color: str = "white") -> None:
    with print_lock:
        log_entries.append(Text(text, style=color))
        if live:
            live.update(render())


class TwitterAccountChecker:
    def __init__(self, config_path: str = "config.json") -> None:
        with open(config_path, "r", encoding="utf-8") as fp:
            self.config = json.load(fp)

        os.makedirs("output", exist_ok=True)
        self.total_accounts = 0
        self.processed_accounts = 0
        self.scanned_accounts = []

    def set_console_title(self) -> None:
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(
                f"Progress: {self.processed_accounts}/{self.total_accounts}"
            )
        except Exception:
            pass

    def get_proxy(self) -> dict:
        proxy = self.config.get("proxy", "")
        return {"http": proxy, "https": proxy}

    def random_line_from_file(self, file_path: str = "tokens.txt") -> str:
        with open(file_path, "r", encoding="utf-8") as fp:
            lines = fp.readlines()
        return random.choice(lines).strip()

    def extract_screen_names(self, file_path: str = "tokens.txt"):
        result = []
        with open(file_path, "r", encoding="utf-8") as fp:
            for line in fp:
                processed = line.strip()
                screen_name = processed.split(":")[0]
                result.append((screen_name, processed))
        self.total_accounts = len(result)
        return result

    def get_twitter_user_info(self, screen_name: str, max_retries: int = 7, retry_delay: float = 1.0):
        url = (
            "https://twitter.com/i/api/graphql/"
            "NimuplG1OB7Fd2btCLdBOw/UserByScreenName"
            "?variables=%7B%22screen_name%22%3A%22"
            f"{screen_name}"
            "%22%2C%22withSafetyModeUserFields%22%3Atrue%7D"
            "&features=%7B%22hidden_profile_likes_enabled%22%3Atrue%2C"
            "%22hidden_profile_subscriptions_enabled%22%3Atrue%2C"
            "%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C"
            "%22verified_phone_label_enabled%22%3Atrue%2C"
            "%22subscriptions_verification_info_is_identity_verified_enabled%22%3Atrue%2C"
            "%22subscriptions_verification_info_verified_since_enabled%22%3Atrue%2C"
            "%22highlights_tweets_tab_ui_enabled%22%3Atrue%2C"
            "%22responsive_web_twitter_article_notes_tab_enabled%22%3Atrue%2C"
            "%22creator_subscriptions_tweet_preview_api_enabled%22%3Atrue%2C"
            "%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Atrue%2C"
            "%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%7D"
            "&fieldToggles=%7B%22withAuxiliaryUserLabels%22%3Afalse%7D"
        )
        auth_token_used = None
        for _ in range(max_retries):
            try:
                token_line = self.random_line_from_file().split(":")
                if len(token_line) != 5:
                    console_log(f"[!] Invalid token format: {token_line}", color="red")
                    continue
                _, _, _, ct0, authToken = token_line
                auth_token_used = authToken
                headers = {
                    "Host": "twitter.com",
                    "Cookie": f"auth_token={authToken}; ct0={ct0}",
                    "X-Csrf-Token": ct0,
                    "Authorization": (
                        "Bearer "
                        "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                        "%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
                    ),
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Content-Type": "application/json",
                }
                resp = requests.get(url, headers=headers, proxies=self.get_proxy(), timeout=15)
                resp.raise_for_status()
                return resp.json(), auth_token_used
            except Exception:
                console_log(f"[!] Request error: {authToken}", color="red")
                time.sleep(retry_delay)
        return None, auth_token_used

    def process_user(self, screen_name: str, processed_line: str, live: Live) -> None:
        try:
            json_data, auth_token = self.get_twitter_user_info(screen_name)
            if not json_data:
                with open("output/suspend.txt", "a", encoding="utf-8") as fp:
                    fp.write(f"{processed_line}\n")
                console_log(f"[!] Failed to retrieve data for {screen_name}", live, color="red")
                self.processed_accounts += 1
                self.set_console_title()
                return

            user = json_data.get("data", {}).get("user", {})
            if not user or user.get("result", {}).get("message") == "User is suspended":
                with open("output/suspend.txt", "a", encoding="utf-8") as fp:
                    fp.write(f"{processed_line}\n")
                console_log(f"[!] Suspended or missing: {screen_name}", live, color="red")
                self.processed_accounts += 1
                self.set_console_title()
                return

            result = user.get("result", {})
            legacy = result.get("legacy", {})
            followers_count = legacy.get("followers_count", 0)
            tweet_count = legacy.get("statuses_count", 0)
            created_at = legacy.get("created_at", "")
            created_year = (
                datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y").year
                if created_at
                else "UNKNOWN"
            )

            cfg = self.config
            if cfg.get("followers", True):
                for key, (min_val, max_val) in cfg.get("follower_ranges", {}).items():
                    if min_val <= followers_count <= max_val:
                        with open(f"output/{key}.txt", "a", encoding="utf-8") as fp:
                            line = processed_line
                            if cfg.get("add_followers", False):
                                line += f":{followers_count}"
                            if cfg.get("add_date", False):
                                line += f":{created_year}"
                            if cfg.get("add_tweet", False):
                                line += f":{tweet_count}"
                            fp.write(f"{line}\n")
                        break

            if cfg.get("date", False) and created_year != "UNKNOWN":
                with open(f"output/{created_year}.txt", "a", encoding="utf-8") as fp:
                    fp.write(f"{processed_line}\n")

            if cfg.get("add_tweet", False) and tweet_count > cfg.get("tweet_count_number", 0):
                with open("output/tweet_count.txt", "a", encoding="utf-8") as fp:
                    fp.write(f"{processed_line}\n")

            if result.get("is_blue_verified", False):
                with open("output/blue.txt", "a", encoding="utf-8") as fp:
                    fp.write(f"{processed_line}\n")

            auth_token_display = auth_token or "UNKNOWN_AUTH"
            console_log(
                f"[+] {auth_token_display} | Followers: {followers_count} | Year: {created_year}",
                live,
                color="green",
            )

            self.scanned_accounts.append(screen_name)
            self.processed_accounts += 1
            self.set_console_title()

        except Exception as e:
            console_log(f"[!] Error processing {screen_name}: {str(e)}", live, color="red")
            self.processed_accounts += 1
            self.set_console_title()

    def run(self, live: Live) -> None:
        names_with_lines = self.extract_screen_names()
        max_threads = self.config.get("thread", 100)
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [
                executor.submit(self.process_user, name, line, live)
                for name, line in names_with_lines
            ]
            for future in as_completed(futures):
                future.result()


def main() -> None:
    checker = TwitterAccountChecker()
    with Live(render(), refresh_per_second=5) as live:
        checker.run(live)
        console_log("[✔] All tasks completed. Press Enter to exit... | If you liked it, Donate: 0x49b5a5E370Dc557C8305590C0014D2d22c19C0e8 ", live, color="yellow")
        time.sleep(0.5)
        live.stop()
    input()


if __name__ == "__main__":
    main()
