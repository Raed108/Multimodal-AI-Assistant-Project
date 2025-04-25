import openai
from typing import List
from pydantic import BaseModel
from response_service.constraints import validate_response
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


# Store conversation history
conversation_history = []


def format_constraints(logicalGroups):
    """
    Format the constraints into a readable string, grouped by logical operators.
    """
    if not logicalGroups:
        return "No constraints provided. Answer the question naturally."
    for group in logicalGroups:
        formatted_constraints = []
        for constraint in group.constraints:
            if constraint.type == "structure":
                if group.operator =="AND":
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
#     Clean up the response based on whether the structure constraint is present.
#     If has_structure_constraint is True, start the text from the first point.
#     Otherwise, return the response as-is.
#     """
#     if has_structure_constraint:
#         # Find the first occurrence of a numbered point (e.g., "1.", "2.") or bullet point (e.g., "-", "*")
#         match = re.search(r"(\d+\.\s|-\s|\*\s|\(\d+\))", response)
#         if match:
#             # Extract the text starting from the first point
#             response = response[match.start():]

#     # Convert (1), (2), etc., to 1., 2., etc.
#     response = re.sub(r'\((\d+)\)', r'\1.', response)

#     # Remove unnecessary symbols like ** and *
#     response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
#     response = re.sub(r'\*(.*?)\*', r'\1', response)

#     # Add new lines before numbered points
#     response = re.sub(r'(\d+\.\s)', r'\n\1', response)

#     # Add new lines after sentences
#     response = response.replace('. ', '.\n\n')

#     # Add new lines after colons
#     response = response.replace(': ', ':\n\n')

#     # Ensure paragraphs have space between them
#     response = re.sub(r"(\.\s)", r".\n\n", response)

#     # Replace * with proper new lines and bullet points
#     response = response.replace("* ", "\n- ").replace("*", "")

#     # Remove excessive new lines
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

# def validate_response(response, logicalGroups):
#     """
#     Validate the response against the logical groups of constraints.
#     Returns:
#         - Boolean indicating if all constraints are satisfied
#         - List of unsatisfied constraints
#     """
#     unsatisfied_constraints = []

#     def evaluate_constraint(constraint):
#         if constraint.type == "structure":
#             numbered_points = re.findall(r'^\s*\d+\.\s+', response, re.MULTILINE)
#             bullet_points = re.findall(r'^\s*[-*]\s+', response, re.MULTILINE)
#             total_points = len(numbered_points) if numbered_points else len(bullet_points)
#             return total_points == int(constraint.value)
#         elif constraint.type == "word_inclusion":
#             return constraint.value.strip().lower() in response.lower()
#         elif constraint.type == "word_exclusion":
#             return constraint.value.strip().lower() not in response.lower()
#         return True

#     all_constraints_satisfied = True
    
#     for group in logicalGroups:
#         group_results = [evaluate_constraint(c) for c in group.constraints]
        
#         if group.operator == "AND":
#             # Check all constraints must be True
#             if not all(group_results):
#                 all_constraints_satisfied = False
#                 # Add only failed constraints
#                 for constraint, result in zip(group.constraints, group_results):
#                     if not result:
#                         unsatisfied_constraints.append({
#                             "operator": "AND",
#                             "constraint": constraint
#                         })
                        
#         elif group.operator == "OR":
#             # Check at least one constraint is True
#             if not any(group_results):
#                 all_constraints_satisfied = False
#                 unsatisfied_constraints.append({
#                     "operator": "OR",
#                     "group_constraints": group.constraints
#                 })
                
#         elif group.operator == "NOT":
#             # Check no constraints are True
#             if any(group_results):
#                 all_constraints_satisfied = False
#                 for constraint, result in zip(group.constraints, group_results):
#                     if result:
#                         unsatisfied_constraints.append({
#                             "operator": "NOT",
#                             "constraint": constraint
#                         })

#     return all_constraints_satisfied, unsatisfied_constraints


def generate_response(question, logicalGroups):
    global conversation_history  # Ensure we keep track of history

     # Check if there is a structure constraint in an AND group
    has_structure_constraint = any(
        any(c.type == "structure" for c in group.constraints)
        for group in logicalGroups if group.operator == "AND"
    )

    # Ensure only one structure constraint exists across all groups
    structure_constraints = [
        c for group in logicalGroups for c in group.constraints
        if c.type == "structure"
    ]
    if len(structure_constraints) > 1:
        raise ValueError("Only one structure constraint is allowed.")

    # Append user question to history
    # conversation_history.append({"role": "user", "content": question})
    conversation_history.append(types.Content(role="user", parts=[types.Part.from_text(text=question)]))

    # chat = client.chat.completions.create(
    #     # model="gpt-3.5-turbo",
    #     # model="nousresearch/deephermes-3-llama-3-8b-preview:free",
    #     # model="google/gemini-2.0-pro-exp-02-05:free",
    #     # model="google/gemini-2.5-pro-exp-03-25:free",
    #     model="google/gemini-2.0-flash-exp:free",
    #     #  model="deepseek/deepseek-chat-v3-0324:free",
    #     # model="deepseek/deepseek-r1:free",

    #     messages=conversation_history
    # )

    chat = client2.models.generate_content(
        model="gemini-2.0-flash", 
        contents=conversation_history,
        config= types.GenerateContentConfig(system_instruction=f"Always follow these rules:\n{format_constraints(logicalGroups)}\n\n"
                f"For example, if one of the constraints is a structure constraint that specifies a certain number of points (e.g., exactly 50), format your response accordingly. Each point should be clearly numbered, like this:\n"
                f"1. First point.\n2. Second point.\n... up to N. Last point (as specified by the constraint).\n")
    )

    print("Raw API Response:", chat)  # Debugging line
    print("-------------------------------------------------------------------") # Debugging line

    # if not chat or not chat.choices:
    #     return "Error: No response from LLM"
    if not chat or not chat.candidates:
        return "Error: No response from LLM"
    
    # response = chat.choices[0].message.content
    response = chat.candidates[0].content.parts[0].text
    
    # Append AI response to history
    # conversation_history.append({"role": "assistant", "content": response})
    conversation_history.append(types.Content(role="assistant", parts=[types.Part.from_text(text=response)]))

    # Check if the structure constraint is present
    # has_structure_constraint = any(constraint.type == "structure" for constraint in constraints)

    return format_response(response, has_structure_constraint)

##############################################################################################################################
def generate_valid_response(question: str, logicalGroups: List[LogicalGroup]) -> dict:
    # global conversation_history  # Keep track of history

    ####################################################
    global conversation_history # Keep track of history
    conversation_history = []  # Reset history for each new request
    
    # Add system message with constraints
    # system_msg = {
    #     "role": "system", 
    #     "content": f"Always follow these rules:\n{format_constraints(logicalGroups)}\n\n"
    #                f"And for example, if there is a structure constraint that requires exactly 50 points, ensure your response has 50 distinct points, each marked with a number like this:\n"
    #                f"1. First point.\n2. Second point.\n... up to 50. Fiftieth point.\n"
    # }

    # conversation_history.append(system_msg)
    ####################################################

     # Check if there is a structure constraint in an AND group
    has_structure_constraint = any(
        any(c.type == "structure" for c in group.constraints)
        for group in logicalGroups if group.operator == "AND"
    )

    # Ensure only one structure constraint exists across all groups
    structure_constraints = [
        c for group in logicalGroups for c in group.constraints
        if c.type == "structure"
    ]
    if len(structure_constraints) > 1:
        raise ValueError("Only one structure constraint is allowed.")

    # Get the first response
    response = generate_response(question, logicalGroups)

    iterationCount = 0

    while True: 

        # Validate the response and get unsatisfied constraints
        is_valid, unsatisfied_constraints = validate_response(response, logicalGroups)
        if is_valid:
            break  # Exit the loop if all constraints are satisfied
        
        iterationCount += 1 
        print("Constraints not satisfied, requesting correction...")
        print("Unsatisfied Constraints:", unsatisfied_constraints)  # Debugging line
        print("-------------------------------------------------------------------") # Debugging line
        print(logicalGroups) # Debugging line


        # Generate a readable constraints list for unsatisfied constraints only
        readable_constraints = format_unsatisfied_constraints(unsatisfied_constraints)

        # Analyze why the constraints are not satisfied
        analysis = analyze_failed_constraints(response, readable_constraints)
        print("-------------------------------------------------------------------") # Debugging line
        print("Analysis of Failed Constraints : ", analysis)  # Debugging line
        print("-------------------------------------------------------------------") # Debugging line


        # # Generate a correction prompt with the analysis
        # correction_prompt = (
        #     f"Your last response: '{response}' did not fully satisfy the constraints. "
        #     f"Here is an analysis of why the constraints are not satisfied:\n\n"
        #     f"{analysis}\n\n"
        #     f"Please revise the response to meet the following constraints:\n\n"
        #     f"{readable_constraints}"
        # )

        # Enhanced correction prompt with an example
        correction_prompt = (
            f"Your last response: '{response}' did not fully satisfy the constraints.\n\n"
            f"Here is an analysis of why the constraints are not satisfied:\n\n"
            f"{analysis}\n\n"
            f"Please revise the response to meet the following constraints:\n\n"
            f"{readable_constraints}\n\n"
            f"For example, if there is a structure constraint that requires exactly 50 points, ensure your response has 50 distinct points, each marked with a number like this:\n"
            f"1. First point.\n2. Second point.\n... up to 50. Fiftieth point.\n"
        )

        # conversation_history.append({"role": "user", "content": correction_prompt})

        conversation_history.append(types.Content(role="user", parts=[types.Part.from_text(text=correction_prompt)]))

        # chat = client.chat.completions.create(
        #     # model="gpt-3.5-turbo",
        #     # model="nousresearch/deephermes-3-llama-3-8b-preview:free",
        #     # model="google/gemini-2.0-pro-exp-02-05:free",
        #     # model="google/gemini-2.5-pro-exp-03-25:free",
        #      model="google/gemini-2.0-flash-exp:free",
        #     #  model="deepseek/deepseek-chat-v3-0324:free",
        #     # model="deepseek/deepseek-r1:free",

        #     messages=conversation_history
        # )

        chat = client2.models.generate_content(
            model="gemini-2.0-flash", 
            contents=conversation_history
    )

        # if not chat or not chat.choices:
        #     print(logicalGroups) # Debugging line
        #     return "Error: No corrected response from LLM"
        if not chat or not chat.candidates:
            print(logicalGroups) # Debugging line
            return "Error: No corrected response from LLM"

        # response = chat.choices[0].message.content
        response = chat.candidates[0].content.parts[0].text
        # conversation_history.append({"role": "assistant", "content": response})

        conversation_history.append(types.Content(role="assistant", parts=[types.Part.from_text(text=response)]))

    # Clean the final valid response
    print("Final Response : ",response) # Debugging line
    # cleaned_response = clean_response_with_llm(response)
    # return format_response(cleaned_response, has_structure_constraint)
    return {"response": format_response(response, has_structure_constraint), "iterationCount": iterationCount}



# def analyze_failed_constraints(response, readable_constraints):
#     """
#     Analyze the response to determine why the unsatisfied constraints are not satisfied.
#     Excludes the 'structure' constraint from the analysis.
#     """
#     # Filter out the 'structure' constraint from the readable_constraints
#     filtered_constraints = []
#     for constraint in readable_constraints.split("\n"):
#         if "points" not in constraint:  # Exclude constraints related to points/structure
#             filtered_constraints.append(constraint)

#     if not filtered_constraints:
#         return "All constraints are satisfied."

#     # Join the filtered constraints into a single string
#     filtered_constraints_str = "\n".join(filtered_constraints)

#     # Prompt to analyze the failed constraints
#     analysis_prompt = (
#         f"Here is a response and a list of constraints that are not satisfied. "
#         f"Please analyze why the response does not satisfy these constraints.\n\n"
#         f"Response:\n{response}\n\n"
#         f"Constraints:\n{filtered_constraints_str}\n\n"
#         f"Explanation:"
#     )

#     # Append the analysis prompt to the conversation history
#     conversation_history.append({"role": "user", "content": analysis_prompt})

#     # Get the analysis from the LLM
#     chat = client.chat.completions.create(
#         # model="gpt-3.5-turbo",
#         # model="nousresearch/deephermes-3-llama-3-8b-preview:free",
#         # model="google/gemini-2.0-pro-exp-02-05:free",
#         # model="google/gemini-2.5-pro-exp-03-25:free",
#          model="google/gemini-2.0-flash-exp:free",
#         #  model="deepseek/deepseek-chat-v3-0324:free",
#         # model="deepseek/deepseek-r1:free",
#         messages=conversation_history
#     )

#     if not chat or not chat.choices:
#         return "Unable to analyze the failed constraints."

#     analysis = chat.choices[0].message.content

#     # Append the analysis to the conversation history
#     conversation_history.append({"role": "assistant", "content": analysis})

#     return analysis


def analyze_failed_constraints(response, readable_constraints):
    """
    Analyze the response to determine why the unsatisfied constraints are not satisfied.
    Includes the 'structure' constraint in the analysis.
    """
    # If there are no constraints to analyze, return a default message
    if not readable_constraints:
        return "No constraints to analyze."

    # Count the number of points in the response for structure constraint analysis
    numbered_points = len(re.findall(r'^\s*\d+\.\s+', response, re.MULTILINE))
    bullet_points = len(re.findall(r'^\s*[-*]\s+', response, re.MULTILINE))
    parenthetical_points = len(re.findall(r'\(\d+\)', response))
    total_points = numbered_points if numbered_points else (bullet_points if bullet_points else parenthetical_points)

    # Analyze structure constraints separately
    structure_analysis = []
    other_constraints = []
    for constraint in readable_constraints.split("\n"):
        if "points" in constraint:
            # Extract the expected number of points from the constraint
            match = re.search(r'exactly (\d+) points', constraint)
            if match:
                expected_points = int(match.group(1))
                structure_analysis.append(
                    f"The constraint '{constraint}' failed because the response has {total_points} points, "
                    f"but it should have exactly {expected_points} points."
                )
        else:
            other_constraints.append(constraint)

    # If there are no other constraints to analyze, return the structure analysis
    if not other_constraints:
        return "\n".join(structure_analysis) if structure_analysis else "No non-structure constraints to analyze."

    # Join the other constraints into a single string
    other_constraints_str = "\n".join(other_constraints)

    # Prompt to analyze the non-structure constraints
    analysis_prompt = (
        f"Here is a response and a list of constraints that are not satisfied. "
        f"Please analyze why the response does not satisfy these constraints.\n\n"
        f"Response:\n{response}\n\n"
        f"Constraints:\n{other_constraints_str}\n\n"
        f"Explanation:"
    )

    # Append the analysis prompt to the conversation history
    # conversation_history.append({"role": "user", "content": analysis_prompt})
    conversation_history.append(types.Content(role="user", parts=[types.Part.from_text(text=analysis_prompt)]))

    # Get the analysis from the LLM
    # chat = client.chat.completions.create(
    #     model="google/gemini-2.0-flash-exp:free",
    #     messages=conversation_history
    # )

    chat = client2.models.generate_content(
        model="gemini-2.0-flash", 
        contents=conversation_history
    )

    # if not chat or not chat.choices:
    #     return "Unable to analyze the failed constraints."

    if not chat or not chat.candidates:
        return "Unable to analyze the failed constraints."

    # analysis = chat.choices[0].message.content
    analysis = chat.candidates[0].content.parts[0].text

    # Append the analysis to the conversation history
    # conversation_history.append({"role": "assistant", "content": analysis})
    conversation_history.append(types.Content(role="assistant", parts=[types.Part.from_text(text=analysis)]))

    # Combine structure analysis with other analysis
    if structure_analysis:
        joined_structure = '\n'.join(structure_analysis)
        analysis = f"Structure Analysis:\n{joined_structure}\n\nOther Constraints Analysis:\n{analysis}"


    return analysis


def format_unsatisfied_constraints(unsatisfied_constraints):
    """
    Format the unsatisfied constraints into a readable string.
    For OR groups, indicate that at least one constraint must be satisfied.
    """
    formatted_constraints = []
    for item in unsatisfied_constraints:
        operator = item["operator"]
        constraint = item.get("constraint")  # Use .get() to avoid KeyError
        group_constraints = item.get("group_constraints")  # Use .get() to avoid KeyError

        if operator == "OR":
            # For OR groups, indicate that at least one constraint must be satisfied
            formatted_constraints.append(
                f"- For the OR group, at least one of the following constraints must be satisfied:"
            )
            # Add all constraints in the OR group
            for c in group_constraints:
                if c.type == "word_inclusion":
                    formatted_constraints.append(f"  - The response must include the word '{c.value}'.")
                elif c.type == "word_exclusion":
                    formatted_constraints.append(f"  - The response must not include the word '{c.value}'.")
        else:
            # For AND and NOT groups, format the individual constraints
            if constraint and constraint.type == "structure":
                formatted_constraints.append(f"- The response must have exactly {constraint.value} points.")
            elif constraint and constraint.type == "word_inclusion":
                if operator == "NOT":
                    formatted_constraints.append(f"- The response must not include the word '{constraint.value}'.")
                else:
                    formatted_constraints.append(f"- The response must include the word '{constraint.value}'.")
            elif constraint and constraint.type == "word_exclusion":
                if operator == "NOT":
                    formatted_constraints.append(f"- The response must include the word '{constraint.value}'.")
                else:
                    formatted_constraints.append(f"- The response must not include the word '{constraint.value}'.")
    return "\n".join(formatted_constraints)