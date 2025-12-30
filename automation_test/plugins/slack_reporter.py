import os

import pytest
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = "#your-channel"

print("Slack reporter plugin loaded.")


def send_slack_message(text, file_path=None):
    client = WebClient(token=SLACK_TOKEN)
    try:
        # Send summary message
        client.chat_postMessage(channel=SLACK_CHANNEL, text=text)
        # Optionally upload the report file
        if file_path and os.path.exists(file_path):
            client.files_upload(
                channels=SLACK_CHANNEL,
                file=file_path,
                title="Test Report",
            )
    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))
    total = passed + failed + skipped
    summary = (
        f"Prodoscore Automation Test Results:\n"
        f"Total: {total}\n"
        f"Passed: {passed}\n"
        f"Failed: {failed}\n"
        f"Skipped: {skipped}\n"
    )
    # # Path to your HTML report
    # report_path = os.path.join(config.rootdir, "reports/html/report.html")
    # send_slack_message(summary, file_path=report_path)
    terminalreporter.write("Slack reporting is currently disabled.\n")
    terminalreporter.write(summary + "\n")
