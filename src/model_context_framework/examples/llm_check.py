from model_context_framework.llms.lmstudio_llm import get_llm

if __name__=="__main__":
    # Load the LLM
    llm = get_llm()
    if llm is None:
        print("LMStudio LLM is not available. Please ensure LMStudio is running and has a model loaded.")
        exit(1)
    
    # Define the prompt
    prompt = "What is the capital of Germany?"
    # Call the LLM with the prompt
    response = llm.invoke(prompt)
    # Print the response
    print(response)