import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai.chat_models import GoogleRateLimitError

from config import GEMINI_API_KEY
from nodes.response_text import response_to_text


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0,
    api_key=GEMINI_API_KEY
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an X post quality evaluator.

Evaluate the post.

Give a score from 1 to 10.

Consider:

1. Hook
2. Value
3. Clarity
4. Engagement
5. Natural writing
6. Character limit
7. Originality

Return exactly:

SCORE: number
FEEDBACK: short feedback
"""
    ),
    (
        "human",
        "{draft}"
    )
])

def evaluate_post(state):
    """Evaluate a tweet draft with retry logic for rate limits."""
    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:
            chain = prompt | llm
            response = chain.invoke({
                "draft": state['draft']
            })

            text = response_to_text(response.content)

            score = 5
            feedback = text

            for line in text.splitlines():
                if line.startswith("SCORE"):
                    try:
                        score = int(line.split(":")[1].strip())
                    except ValueError:
                        pass
                elif line.startswith("FEEDBACK:"):
                    feedback = line.split(":", 1)[1].strip()

            return {
                "score": score,
                "feedback": feedback
            }
        except GoogleRateLimitError as e:
            attempt += 1
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                print(f"[Evaluator] Rate limited (429). Attempt {attempt}/{max_retries}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[Evaluator] Rate limit exceeded after {max_retries} attempts. Using default score.")
                # Fallback to default score if all retries fail
                return {
                    "score": 6,
                    "feedback": "Fallback evaluation due to rate limit"
                }
        except Exception as e:
            print(f"[Evaluator] Error evaluating post: {e}")
            raise
