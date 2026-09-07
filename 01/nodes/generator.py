from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from config import GEMINI_API_KEY

llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.8,api_key=GEMINI_API_KEY)


prompt=ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert X/Twitter content creator.

Create an engaging X post about the given topic.

Rules:

- Maximum 280 characters.
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
    )


])


def generate_post(state):
    """Generate a tweet draft with retry and fallback handling.
    Tries up to 3 times with the primary model (gemini-2.5-flash). If a
    503 "high demand" error occurs, it falls back to the cheaper
    "gemini-1.5-flash" model and retries again. This makes the pipeline
    more robust in CI/GitHub Actions where transient rate‑limits are
    common.
    """
    global llm
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
            return {"draft": response.content.strip(), "attempts": state.get("attempts", 0) + 1}
        except Exception as e:
            # Handle GoogleAPIError 503 specifically
            from langchain_google_genai.chat_models import GoogleAPIError
            if isinstance(e, GoogleAPIError) and getattr(e, "args", None):
                error_info = e.args[0].get('error', {}) if isinstance(e.args[0], dict) else {}
                if error_info.get('code') == 503:
                    attempt += 1
                    print(f"[Generator] Gemini model unavailable (attempt {attempt}/{max_retries}). Retrying in 5s...")
                    import time
                    time.sleep(5)
                    if attempt == 2:
                        print("[Generator] Switching to fallback model 'gemini-1.5-flash'.")
                        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.8, api_key=GEMINI_API_KEY)
                    continue
            raise
    raise RuntimeError("Failed to generate post after multiple retries due to Gemini API availability.")
