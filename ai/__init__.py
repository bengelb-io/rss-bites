from openai import OpenAI
from db import Entry

client = OpenAI()

template = """
**Task**: Write a fun summary on the provided article about {description}.
**Input**: Below is an article titled "{title}" by HBR.
[{article}]
**Instructions**:
- Focus on capturing the main ideas and key arguments presented in the article.
- Provide a concise summary in your own words, highlight interesting details.
- Structure the summary into introduction, body, and conclusion.
- Ensure coherence and clarity in the summary.
- Use exciting language and maintain a upbeat tone.
- Avoid including personal opinions or interpretations.
**Length**: 500-750 words.
""".strip()


def summarize(entry: Entry, article: str) -> str:
    prompt = template.format(
        title=entry.title, description=entry.description, article=article
    )
    completions = client.chat.completions.create(model="gpt-4o", messages=[{
        "role": "user",
        "content": prompt
    }])
    if completions.choices[0].message.content:
        return completions.choices[0].message.content
    raise Exception()
