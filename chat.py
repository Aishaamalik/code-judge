from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import os

def create_chat_chain(temperature: float = 0.7):
    """Create a conversation chain for chatting about code."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=temperature,  # Configurable temperature for conversational responses
    )

    # Create a prompt template for code-related conversations
    prompt_template = """You are an expert AI assistant specializing in code analysis, programming, and software development. You help users understand, improve, and discuss their code.

Current conversation:
{history}

Human: {input}
Assistant: """

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=prompt_template,
    )

    # Create conversation chain with memory
    memory = ConversationBufferMemory(return_messages=True)
    chain = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=False
    )

    return chain

def send_message(chain, message):
    """Send a message to the chat chain and get response."""
    try:
        response = chain.predict(input=message)
        return response
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
