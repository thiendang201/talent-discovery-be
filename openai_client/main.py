from openai import OpenAI
from configs import env_configs
from .parse_resume_templates import resumeTemplate3

apiKey = env_configs.get("OPENAI_API_KEY")
client = OpenAI(api_key=apiKey)


def get_embedding(content: str):
    response = client.embeddings.create(input=content, model="text-embedding-ada-002")
    return response.data[0].embedding


def parseResume(textContent: str, model="gpt-3.5-turbo-1106"):
    systemMessage = {
        "role": "system",
        "content": f"""You will be provided with text.\
            If it contains information about a resume then summarize the information into a JSON with exactly the following structure: {resumeTemplate3}. \
            If the text does not contain information of a resume, then simply write None instead JSON schema.""",
    }
    messages = [systemMessage, {"role": "user", "content": textContent}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )

    return response.choices[0].message.content
