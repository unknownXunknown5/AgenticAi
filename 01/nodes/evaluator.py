from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

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