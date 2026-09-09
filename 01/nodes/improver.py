import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai.chat_models import GoogleRateLimitError

from config import GEMINI_API_KEY
from nodes.response_text import response_to_text


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.7,
    api_key=GEMINI_API_KEY
)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You improve X/Twitter posts.

Rewrite the post using the evaluator feedback.

Rules:

- Maximum 280 characters.
- Keep the original idea.
- Make the hook stronger.
- Make it useful.
- Make it sound human.
- Don't add fake facts.
- Don't add unnecessary hashtags.
- Return ONLY the final post.
"""
    ),
    (
        "human",
        """
Current post:

{draft}

Evaluator feedback:

{feedback}
"""
    )
])


def improve_post(state):
    """Improve a tweet draft with retry logic for rate limits."""
    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:
            chain = prompt | llm

            response = chain.invoke({
                "draft": state["draft"],
                "feedback": state["feedback"]
            })

            return {
                "draft": response_to_text(response.content)
            }
        except GoogleRateLimitError as e:
            attempt += 1
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                print(f"[Improver] Rate limited (429). Attempt {attempt}/{max_retries}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[Improver] Rate limit exceeded after {max_retries} attempts. Returning original draft.")
                # Fallback: return the original draft if all retries fail
                return {
                    "draft": state["draft"]
                }
        except Exception as e:
            print(f"[Improver] Error improving post: {e}")
            raise
