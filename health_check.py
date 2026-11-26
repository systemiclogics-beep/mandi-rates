"""Daily cloud health check for BharatMandi live CDN endpoints."""

from collections import Counter
import datetime
import json
import os
import sys
import urllib.request

TODAY_URL = "https://cdn.jsdelivr.net/gh/systemiclogics-beep/mandi-rates@data/today.json"
WEATHER_URL = "https://cdn.jsdelivr.net/gh/systemiclogics-beep/mandi-rates@data/weather.json"
MAX_BYTES = 5 * 1024 * 1024  # 5.0 MB mobile limit


def fetch_json(url: str, timeout: int = 20) -> tuple[dict, int]:
    """Fetch JSON from URL and return (parsed_dict, byte_size)."""
    req = urllib.request.Request(url, headers={"User-Agent": "BharatMandi-HealthCheck/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} from {url}")
        raw = resp.read()
        return json.loads(raw.decode("utf-8")), len(raw)


def main() -> int:
    today_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%d-%m-%Y")
    issues: list[str] = []

    today_data, today_bytes = fetch_json(TODAY_URL)
    today_mb = today_bytes / (1024 * 1024)
    records = today_data.get("records", [])
    generated_at = str(today_data.get("generated_at", ""))
    fresh_count = Counter(r.get("arrival_date") for r in records).get(today_utc, 0)

    if today_bytes > MAX_BYTES:
        issues.append(f"today.json size {today_mb:.2f} MB exceeds 5.0 MB limit")
    if len(records) < 1000:
        issues.append(f"today.json only has {len(records)} records")
    if not generated_at.startswith(today_utc):
        issues.append(f"today.json stale (generated_at={generated_at}, expected {today_utc})")

    weather_data, weather_bytes = fetch_json(WEATHER_URL)
    weather_kb = weather_bytes / 1024
    locations = weather_data.get("total_locations", len(weather_data.get("weather", {})))
    if locations < 150:
        issues.append(f"weather.json only has {locations} locations")

    status_icon = "✅" if not issues else "🚨"
    summary_lines = [
        f"{status_icon} BharatMandi Daily Check ({today_utc})",
        f"• Rates: {len(records):,} total ({fresh_count:,} fresh today) | {today_mb:.2f} MB | {generated_at}",
        f"• Weather: {locations} locations | {weather_kb:.1f} KB",
    ]
    if issues:
        summary_lines.append("• Issues: " + "; ".join(issues))

    summary_text = "\n".join(summary_lines)
    print(summary_text)

    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as f:
            f.write("HEALTH_MSG<<EOF\n" + summary_text + "\nEOF\n")

    github_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_summary:
        with open(github_summary, "a", encoding="utf-8") as f:
            f.write("### " + summary_lines[0] + "\n\n" + "\n".join(summary_lines[1:]) + "\n")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
