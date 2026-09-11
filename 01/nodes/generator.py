import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai.chat_models import GoogleRateLimitError

from config import GEMINI_API_KEY
from nodes.response_text import response_to_text

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    # temperature=0.8, temperature 3.6 me pahkle se hi hota hai
    api_key=GEMINI_API_KEY,
)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert X/Twitter content creator.

Create an engaging X post about the given topic.

Rules:

- Maximum 250 characters.
- Strong opening hook.
- Useful information.
- Natural language.
- Do not sound like an AI.
- Avoid unnecessary hashtags.
- Avoid fake statistics.
- Do not make unsupported claims.
- Do not use clickbait.
- Keep it readable.
"""
    ),
    (
        "human",
        """
Topic: {topic}

Audience: {audience}

Tone: {tone}

Create the post.
"""
    ),
])


def generate_post(state):
    """Generate a tweet draft with retry logic for rate limits.

    Returns a dictionary with the draft text and the number of attempts."""
    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:
            chain = prompt | llm
            response = chain.invoke({
                "topic": state["topic"],
                "audience": state["audience"],
                "tone": state["tone"]
            })
            draft = " ".join(response_to_text(response.content).split())
            if len(draft) > 250:
                draft = draft[:277].rsplit(" ", 1)[0] + "..."
            print(f"[Generator] Draft generated: {draft}")
            return {"draft": draft, "attempts": 1}
        except GoogleRateLimitError as e:
            attempt += 1
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                print(f"[Generator] Rate limited (429). Attempt {attempt}/{max_retries}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[Generator] Rate limit exceeded after {max_retries} attempts. Falling back to generic post.")
                # Fallback to a generic post if all retries fail
                return {
                    "draft": f"Exploring: {state['topic'][:230]}",
                    "attempts": 1
                }
        except Exception as e:
            print(f"[Generator] Error generating post: {e}")
            raise
