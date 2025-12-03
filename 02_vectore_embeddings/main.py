from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()

client = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key=os.getenv("API_KEY")
)

text = "dog chases cat"

response = client.embeddings.create(
    input=text,
    model="text-embedding-3-small"
)

print("V.embeddings : ",response.data[0].embedding)
print("length of V.embeddings : ", len(response.data[0].embedding))

# the length of the vector embeddings tells us the exact pin point location of this text "dog chases cat" which we have given.
# So we got the output of the length as 1536 so its a 1536 Dimensional aread. in which the vector embeddings of this text which we have given are stored