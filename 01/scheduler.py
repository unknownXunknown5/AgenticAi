import argparse
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import POST_HOURS, POST_MINUTE, TIMEZONE
from nodes.graph import graph


def run_agentic_tweet():
    """Executes the full agentic AI pipeline to generate, evaluate, and post a tweet."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now_str}] 🚀 Triggering Agentic AI Tweet Pipeline...")

    try:
        result = graph.invoke({"attempts": 0})

        print("\n==============================")
        print("TOPIC")
        print("==============================")
        print(result.get("topic"))

        print("\n==============================")
        print("POST")
        print("==============================")
        print(result.get("final_post"))

        print("\n==============================")
        print("SCORE")
        print("==============================")
        print(result.get("score"))

        print("\n==============================")
        print("TWEET STATUS")
        print("==============================")
        print(f"URL: {result.get('tweet_url')}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Tweet published successfully!\n")

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error during execution: {e}\n")


def start_scheduler(run_now: bool = False):
    """Starts the daily 3-tweet scheduler."""
    print("==================================================")
    print("🤖 Agentic AI Daily Tweet Scheduler")
    print("==================================================")
    print(f"Timezone: {TIMEZONE}")
    print(f"Daily Target: {len(POST_HOURS)} tweets per day")
    print(f"Scheduled Times: {', '.join([f'{h:02d}:{POST_MINUTE:02d}' for h in POST_HOURS])}")
    print("==================================================")

    if run_now:
        print("\n⚡ Option '--now' detected: Running agentic chain once immediately...")
        run_agentic_tweet()

    scheduler = BlockingScheduler(timezone=TIMEZONE)

    for hour in POST_HOURS:
        trigger = CronTrigger(hour=hour, minute=POST_MINUTE, timezone=TIMEZONE)
        job_id = f"tweet_job_{hour:02d}_{POST_MINUTE:02d}"
        scheduler.add_job(
            run_agentic_tweet,
            trigger=trigger,
            id=job_id,
            name=f"Daily Tweet at {hour:02d}:{POST_MINUTE:02d}"
        )
        print(f"✓ Registered job: Daily at {hour:02d}:{POST_MINUTE:02d} ({TIMEZONE})")

    print("\n⏳ Scheduler is active and waiting for the next trigger...")
    print("Press Ctrl+C to stop.\n")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Scheduler stopped cleanly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic AI Tweet Scheduler")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Run the agentic chain once immediately before waiting for the scheduled times"
    )
    args = parser.parse_args()

    start_scheduler(run_now=args.now)
