from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from config import GEMINI_API_KEY
llm=ChatGoogleGenerativeAI(model='gemini-2.5-flash',temperature=0,)  # 0 to 0.3 determinitic and predictable but 0.8 to 1 randomness,dversity and creativeness jada hota hai

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
    chain=prompt | llm
    response=chain.invoke({
        "draft":state['draft']
    })

    text =response.content.strip()

    score=5
    feedback=text

    for line in text.splitlines():
        if line.startswith("SCORE"):
            try:
                score=int(line.split(":")[1].strip())
            except ValueError:
                pass

        elif line.startswith("FEEDBACK:"):
            feedback=line.split(":",1)[1].strip() #It extracts the text after "FEEDBACK:" and stores it in feedback.

        return {
        "score": score,
        "feedback": feedback
    }    