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
    chain=prompt | llm 
    response=chain.invoke({
         "topic": state["topic"],
        "audience": state["audience"],
        "tone": state["tone"]
    })

    return {
        "draft": response.content.strip(),
        "attempts": state.get("attempts", 0) + 1
    }
