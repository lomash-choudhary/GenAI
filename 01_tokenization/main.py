import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")

text = "Hello my name is lomash"

tokens = encoder.encode(text)

print("tokens : ", tokens)

createdTokens =  [13225, 922, 1308, 382, 60495, 1229]

text_from_tokens = encoder.decode(createdTokens)

print("decoded text : ", text_from_tokens)