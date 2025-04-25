import openai
from typing import List
from pydantic import BaseModel
import re
from google import genai
from google.genai import types
import os 
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Constraint(BaseModel):
    type: str
    value: str

class LogicalGroup(BaseModel):
    operator: str  # AND, OR, NOT
    constraints: List[Constraint]

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

client2 = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

conversation_history = []
conversation_history_openai = []
conversation_history_gemini = []


def format_constraints(logicalGroups):
    """
    Format the constraints into a readable string, grouped by logical operators.
    """
    if not logicalGroups:
        return "No constraints provided. Answer the question naturally."
    formatted_constraints = []
    for group in logicalGroups:
        for constraint in group.constraints:
            if constraint.type == "structure" and group.operator == "AND":
                formatted_constraints.append(f"- The response must have exactly {constraint.value} points.")
            elif constraint.type == "word_inclusion":
                if group.operator == "NOT":
                    formatted_constraints.append(f"- The response must not include the word '{constraint.value}'.")
                else:
                    formatted_constraints.append(f"- The response must include the word '{constraint.value}'.")
            elif constraint.type == "word_exclusion":
                if group.operator == "NOT":
                    formatted_constraints.append(f"- The response must include the word '{constraint.value}'.")
                else:
                    formatted_constraints.append(f"- The response must not include the word '{constraint.value}'.")
    return "\n\n".join(formatted_constraints)

# def format_response(response, has_structure_constraint):
#     """
#     Clean up the response based on whether a structure constraint is present.
#     """
#     if has_structure_constraint:
#         match = re.search(r"(\d+\.\s|-\s|\*\s)", response)
#         if match:
#             response = response[match.start():]
#     response = re.sub(r'#+\s*', '', response)
#     response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
#     response = re.sub(r'\*(.*?)\*', r'\1', response)
#     response = re.sub(r'(\d+\.\s)', r'\n\1', response)
#     response = response.replace('. ', '.\n\n').replace(': ', ':\n\n')
#     response = re.sub(r"(\.\s)", r".\n\n", response)
#     response = response.replace("* ", "\n- ").replace("*", "")
#     response = re.sub(r'(\n\s*)+', r'\n', response)
#     return response.strip()

def format_response(response, has_structure_constraint):
    """
    Clean up the response based on whether the structure constraint is present.
    If has_structure_constraint is True, start the text from the first point.
    Otherwise, return the response as-is.
    """
    if has_structure_constraint:
        # Find the first point that starts with "1.", or a bullet point, ignoring numbers in headers
        match = re.search(r'^(?:\s*\d+\.\s+|\s*[-*]\s+|\s*\(\d+\))', response, re.MULTILINE)
        if match:
            response = response[match.start():]
        else:
            # If no points are found, return the response as-is to avoid losing content
            pass

    # Convert (1), (2), etc., to 1., 2., etc.
    response = re.sub(r'\((\d+)\)', r'\1.', response)

    # Remove unnecessary symbols like ** and *
    response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
    response = re.sub(r'\*(.*?)\*', r'\1', response)

    # Add new lines before numbered points
    response = re.sub(r'(\d+\.\s)', r'\n\1', response)

    # Add new lines after sentences
    response = response.replace('. ', '.\n\n')

    # Add new lines after colons
    response = response.replace(': ', ':\n\n')

    # Ensure paragraphs have space between them
    response = re.sub(r"(\.\s)", r".\n\n", response)

    # Replace * with proper new lines and bullet points
    response = response.replace("* ", "\n- ").replace("*", "")

    # Remove excessive new lines
    response = re.sub(r'(\n\s*)+', r'\n', response)

    return response.strip()

def generate_response_model(question, logicalGroups, model_name):
    """
    Generalized function to generate a response from a specified model.
    """
    global conversation_history_openai
    global conversation_history_gemini 

    has_structure_constraint = any(
        any(c.type == "structure" for c in group.constraints)
        for group in logicalGroups if group.operator == "AND"
    )
    structure_constraints = [
        c for group in logicalGroups for c in group.constraints if c.type == "structure"
    ]
    if len(structure_constraints) > 1:
        raise ValueError("Only one structure constraint is allowed.")
    if model_name == "deepseek/deepseek-r1:free":
        conversation_history_openai.append({"role": "user", "content": question})
        chat = client.chat.completions.create(
            model=model_name,
            messages=conversation_history_openai
        )
        print("Raw API Response:", chat)
        print("-------------------------------------------------------------------")
        if not chat or not chat.choices:
            return "Error: No response from LLM"
        response = chat.choices[0].message.content
        conversation_history_openai.append({"role": "assistant", "content": response})
    else:
        conversation_history_gemini.append(types.Content(role="user", parts=[types.Part.from_text(text=question)]))
        chat = client2.models.generate_content(
            model=model_name, 
            contents=conversation_history_gemini,
            config= types.GenerateContentConfig(system_instruction=f"Always follow these rules:\n{format_constraints(logicalGroups)}")
        )
        print("Raw API Response:", chat)
        print("-------------------------------------------------------------------")
        if not chat or not chat.candidates:
            return "Error: No response from LLM"
        response = chat.candidates[0].content.parts[0].text
        conversation_history_gemini.append(types.Content(role="assistant", parts=[types.Part.from_text(text=response)]))

    return format_response(response, has_structure_constraint)

def generate_response_A(question, logicalGroups):
    return generate_response_model(question, logicalGroups, "gemini-2.0-flash")

def generate_response_B(question, logicalGroups):
    return generate_response_model(question, logicalGroups, "deepseek/deepseek-r1:free")

def analyze_response(response, model_name):
    """
    Analyze a response using the specified model with a detailed prompt.
    """
    global conversation_history_openai
    global conversation_history_gemini 

#     analysis_prompt = (
#     f"What about this response? Please provide a detailed analysis:\n\n"
#     f"Response:\n{response}\n\n"
#     f"Use the following format for your analysis:\n"
#     f"STRENGTHS:\n- [Point 1]\n- [Point 2]\n"
#     f"WEAKNESSES:\n- [Point 1]\n- [Point 2]\n"
#     f"POTENTIAL IMPROVEMENTS:\n- [Point 1]\n- [Point 2]\n\n"
#     f"- Is the response clear and well-structured?\n"
#     f"- Does it appear to address the original question effectively?\n"
#     f"- Are there any potential improvements or refinements that could be made?\n"
#     f"- Highlight any strengths or weaknesses you observe.\n\n"
#     f"Provide your feedback below:"
# )

    analysis_prompt = (
        f"What about this response? Please provide a detailed analysis:\n\n"
        f"Response:\n{response}\n\n"
        f"Use the following format for your analysis:\n"
        f"STRENGTHS:\n- [Point 1]\n- [Point 2]\n\n"
        f"WEAKNESSES:\n- [Point 1]\n- [Point 2]\n\n"
        f"POTENTIAL IMPROVEMENTS:\n- [Point 1]\n- [Point 2]\n\n"
        f"ANALYSIS OF QUESTIONS:\n"
        f"1. Is the response clear and well-structured?\n"
        f"2. Does it appear to address the original question effectively?\n"
        f"3. Are there any potential improvements or refinements that could be made?\n"
        f"4. Highlight any strengths or weaknesses you observe.\n\n"
        f"Provide your feedback below, ensuring all sections (STRENGTHS, WEAKNESSES, POTENTIAL IMPROVEMENTS, ANALYSIS OF QUESTIONS) are included, even if empty:"
    )

    if model_name == "deepseek/deepseek-r1:free":
        conversation_history_openai.append({"role": "user", "content": analysis_prompt})
        chat = client.chat.completions.create(
            model=model_name,
            messages=conversation_history_openai
        )
        if not chat or not chat.choices:
            return "Error: No analysis from LLM"
        
        analysis = chat.choices[0].message.content

        conversation_history_openai.append({"role": "assistant", "content": analysis})
    else:
        conversation_history_gemini.append(types.Content(role="user", parts=[types.Part.from_text(text=analysis_prompt)]))
        chat = client2.models.generate_content(
            model=model_name, 
            contents=conversation_history_gemini,
        )
        if not chat or not chat.candidates:
            return "Error: No analysis from LLM"
        
        analysis = chat.candidates[0].content.parts[0].text
        conversation_history_gemini.append(types.Content(role="assistant", parts=[types.Part.from_text(text=analysis)]))
    return format_response(analysis, True)

    # # Ensure all sections are present
    # sections = ["STRENGTHS:", "WEAKNESSES:", "POTENTIAL IMPROVEMENTS:", "ANALYSIS OF QUESTIONS:"]
    # formatted_analysis = ""
    # current_analysis = analysis

    # for section in sections:
    #     if section not in current_analysis.upper():
    #         formatted_analysis += f"\n\n{section}\n- None identified."
    #     else:
    #         # Extract the section content until the next section or end
    #         start_idx = current_analysis.upper().find(section)
    #         end_idx = len(current_analysis)
    #         for next_section in sections:
    #             if next_section != section:
    #                 next_idx = current_analysis.upper().find(next_section, start_idx + len(section))
    #                 if next_idx != -1 and next_idx < end_idx:
    #                     end_idx = next_idx
    #         section_content = current_analysis[start_idx:end_idx].strip()
    #         formatted_analysis += f"\n\n{section_content}"

    # conversation_history.append({"role": "assistant", "content": formatted_analysis})
    # return format_response(formatted_analysis, True)

def generate_valid_response(question: str, logicalGroups: List[LogicalGroup]) -> dict:
    """
    Generate two responses from different models and perform cross-model analysis.
    """
    global conversation_history_openai
    global conversation_history_gemini 
    conversation_history_openai = []
    conversation_history_gemini = []
    system_msg = {
        "role": "system",
        "content": f"Always follow these rules:\n{format_constraints(logicalGroups)}"
    }
    conversation_history_openai.append(system_msg)

    # Generate initial responses
    response_A = generate_response_A(question, logicalGroups)
    response_B = generate_response_B(question, logicalGroups)

    # Perform cross-model analysis
    analysis_B_of_A = analyze_response(response_A, "deepseek/deepseek-r1:free")
    analysis_A_of_B = analyze_response(response_B, "gemini-2.0-flash")

    # Return both responses and their analyses
    return {
        "response_A": response_A,
        "response_B": response_B,
        "analysis_B_of_A": analysis_B_of_A,
        "analysis_A_of_B": analysis_A_of_B
    }