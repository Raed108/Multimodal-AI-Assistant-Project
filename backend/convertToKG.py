import openai
from fastapi import HTTPException
from typing import List
from pydantic import BaseModel
import re
from google import genai
from google.genai import types
import os 
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file



client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

client2 = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


conversation_history = []

def call_llm_api(prompt: str) -> str:
    """
    Call the LLM API to generate a response for the given prompt using OpenAI via OpenRouter.
    """
    global conversation_history
    # Reset conversation history for each new request
    conversation_history = []
    
    # System message to set up the LLM's behavior
    # system_msg = {
    #     "role": "system",
    #     "content": (
            # "You are a helpful assistant that extracts knowledge graphs from text. "
            # "You will be provided with a text and you need to extract the knowledge graph in the form of triples. "
            # "The triples should be in the format (entity1, relation, entity2). "
            # "You should only return the triples, one per line, in the format (entity1, relation, entity2)."
    #     )
    # }
    # conversation_history.append(system_msg)


    # Add the user prompt to the conversation history
    # conversation_history.append({"role": "user", "content": prompt})
    user_msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    conversation_history.append(user_msg)

    try:
        # Call the OpenAI API (via OpenRouter)
        # chat = client.chat.completions.create(
        #     model="google/gemini-2.0-flash-exp:free",
        #     messages=conversation_history
        # )
        # result = chat.choices[0].message.content.strip()

        chat = client2.models.generate_content(
            model="gemini-2.0-flash", 
            contents=conversation_history,
            config= types.GenerateContentConfig(system_instruction="You are a helpful assistant that extracts knowledge graphs from text."
                "You will be provided with a text and you need to extract the knowledge graph in the form of triples. "
                "The triples should be in the format (entity1, relation, entity2). "
                "You should only return the triples, one per line, in the format (entity1, relation, entity2).")
        )
        result = chat.candidates[0].content.parts[0].text.strip()

        # Append the LLM's response to the conversation history
        # conversation_history.append({"role": "assistant", "content": result})
        assistant_msg = types.Content(role="assistant", parts=[types.Part.from_text(text=result)])
        conversation_history.append(assistant_msg)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM API call failed: {str(e)}")



def parse_triples(llm_output: str) -> List[List[str]]:
    """
    Parse the LLM output into a list of triples [entity1, relation, entity2].
    """
    try:
        # Expected format: (entity1, relation, entity2) per line
        triples = []
        # Match patterns like (entity1, relation, entity2)
        pattern = r"\(([^,]+),\s*([^,]+),\s*([^\)]+)\)"
        for match in re.finditer(pattern, llm_output):
            entity1, relation, entity2 = match.groups()
            triples.append([entity1.strip(), relation.strip(), entity2.strip()])
        if not triples:
            return []
        return triples
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse triples: {str(e)}")
    

def extract_knowledge_graph(response: str) -> List[List[str]]:
    """
    Extract a knowledge graph from the response text using an LLM.
    Returns a list of triples [entity1, relation, entity2].
    """
    # Define the prompt for the LLM
    prompt = (
        "Extract a knowledge graph from the following text in the form of triples: (entity1, relation, entity2).\n"
        "Each triple should represent a relationship between two entities.\n"
        "Return the triples as a list, one per line, in the format (entity1, relation, entity2).\n\n"
        f"Text:\n{response}\n\n"
        "Triples:"
    )

    # Use the real LLM API call
    llm_output = call_llm_api(prompt)

    triples = parse_triples(llm_output)
    return triples
