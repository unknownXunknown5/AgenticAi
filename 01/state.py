from typing import TypedDict

class PostState(TypedDict, total=False):
    topic: str
    audience: str
    tone: str

    draft: str
    feedback: str
    score: int

    attempts: int

    final_post: str

    tweet_id: str
    tweet_url: str

    error: str