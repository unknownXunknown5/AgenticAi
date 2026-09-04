import requests

from config import X_ACCESS_TOKEN


def publish_to_x(state):

    if not X_ACCESS_TOKEN:
        raise RuntimeError(
            "X_ACCESS_TOKEN is missing from .env"
        )

    post = state["final_post"]

    response = requests.post(
        "https://api.x.com/2/tweets",
        headers={
            "Authorization": f"Bearer {X_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "text": post
        },
        timeout=30
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"X API error {response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    tweet_id = data["data"]["id"]

    return {
        "tweet_id": tweet_id,
        "tweet_url": f"https://x.com/i/web/status/{tweet_id}"
    }