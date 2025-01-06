# discarded code

# get phrase from local LLM
def getAIphrase():
    print("getting phrase from LLM")
    # set a seed for the LLM
    set_seed(random.randint(0, 1000))
    llm = pipeline(task="text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")
    messages = [
        {
            "role": "system", 
            "content": "You are part of a game of Hangman, providing a short phrase for the participant to guess. Your response must be in the form of a short English phrase. The phrase must be a common phrase, expression, or idiom and must be a single independent clause. Do not use any punctuation. Do not use contractions. Do not user apostrophes, commas, or periods. Only put a single space between words. The response must be in the form of an all-lowercase short phrase. Respond with the phrase and nothing else. Do not respond with the prompt. Only respond with the phrase once. The independent clause must be shorter than 5 words and be complete. The phrase must no include dependent clauses. The phrase must be easy to guess."
        }, 
        {
            "role": "user", 
            "content": "Generate the phrase."
        }
    ]
    prompt = llm.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = llm(prompt, max_new_tokens=10, do_sample=True, temperature=random.uniform(0.3, 0.9), top_k=50, top_p=0.95)
    print(outputs[0]["generated_text"].replace("<|system|>\n" + messages[0]["content"] +"</s>\n<|user|>\nGenerate the phrase.</s>\n<|assistant|>\n", "").strip())
    # return outputs[0]["generated_text"]

# get phrase from HuggingFace serverless inference API
def getAPIphrase() -> str:
    print("getting phrase from LLM on HuggingFace serverless API")
    # authenticate
    client = InferenceClient(api_key="your HuggingFace account comes with 1000 free requests")
    # prompt
    messages = [
        {
            "role": "system", 
            "content": "You are part of a game of Hangman, providing a short phrase for the participant to guess. Your response must be in the form of a short English phrase. The phrase must be a common phrase, expression, or idiom and must be a single independent clause. Do not use any punctuation. Do not use contractions. Do not user apostrophes, commas, or periods. Only put a single space between words. The response must be in the form of an all-lowercase short phrase. Respond with the phrase and nothing else. Do not respond with the prompt. Only respond with the phrase once. The independent clause must be shorter than 5 words and be complete. The phrase must no include dependent clauses. The phrase must be easy to guess."
        }, 
        {
            "role": "user", 
            "content": "Generate the phrase."
        }
    ]
    # call the API
    completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3", 
        messages=messages, 
        max_tokens=500,
        # for extra randomness
        temperature=random.uniform(0.3, 1.0),
    )
    # return the response
    return completion.choices[0].message.content