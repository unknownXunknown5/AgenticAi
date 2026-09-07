from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from config import GEMINI_API_KEY
from nodes.response_text import response_to_text

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.8,
    api_key=GEMINI_API_KEY,
)


prompt = ChatPromptTemplate.from_messages([
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
    ),
])


def generate_post(state):
    """Generate a tweet draft.

    Returns a dictionary with the draft text and the number of attempts (always 1 in this simple version)."""
    try:
        chain = prompt | llm
        response = chain.invoke({
            "topic": state["topic"],
            "audience": state["audience"],
            "tone": state["tone"]
        })
        draft = " ".join(response_to_text(response.content).split())
        if len(draft) > 280:
            draft = draft[:277].rsplit(" ", 1)[0] + "..."
        print(f"[Generator] Draft generated: {draft}")
        return {"draft": draft, "attempts": 1}
    except Exception as e:
        print(f"[Generator] Error generating post: {e}")
        raise
