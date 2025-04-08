from llms.lmstudio_llm import get_llm

if __name__=="__main__":
    # Load the LLM
    llm = get_llm()
    # Define the prompt
    prompt = "What is the capital of Germany?"
    # Call the LLM with the prompt
    response = llm.invoke(prompt) #type: ignore
    # Print the response
    print(response)