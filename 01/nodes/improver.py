from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from config import GEMINI_API_KEY


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
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

    chain = prompt | llm

    response = chain.invoke({
        "draft": state["draft"],
        "feedback": state["feedback"]
    })

    return {
        "draft": response.content.strip()
    }