import re


def validate_response(response, logicalGroups):
    """
    Validate the response against the logical groups of constraints.
    Returns:
        - Boolean indicating if all constraints are satisfied
        - List of unsatisfied constraints
    """
    unsatisfied_constraints = []

    def evaluate_constraint(constraint):
        if constraint.type == "structure":
            # Check for points in multiple formats: "1. ", "- ", "* ", or "(1)"
            numbered_points = re.findall(r'^\s*\d+\.\s+', response, re.MULTILINE)
            bullet_points = re.findall(r'^\s*[-*]\s+', response, re.MULTILINE)
            parenthetical_points = re.findall(r'\(\d+\)', response)
            total_points = len(numbered_points) if numbered_points else (len(bullet_points) if bullet_points else len(parenthetical_points))
            print(f"Found {total_points} points in response")  # Debugging
            return total_points == int(constraint.value)
        elif constraint.type == "word_inclusion":
            return constraint.value.strip().lower() in response.lower()
        elif constraint.type == "word_exclusion":
            return constraint.value.strip().lower() not in response.lower()
        return True

    all_constraints_satisfied = True
    
    for group in logicalGroups:
        group_results = [evaluate_constraint(c) for c in group.constraints]
        
        if group.operator == "AND":
            # Check all constraints must be True
            if not all(group_results):
                all_constraints_satisfied = False
                # Add only failed constraints
                for constraint, result in zip(group.constraints, group_results):
                    if not result:
                        unsatisfied_constraints.append({
                            "operator": "AND",
                            "constraint": constraint
                        })
                        
        elif group.operator == "OR":
            # Check at least one constraint is True
            if not any(group_results):
                all_constraints_satisfied = False
                unsatisfied_constraints.append({
                    "operator": "OR",
                    "group_constraints": group.constraints
                })
                
        elif group.operator == "NOT":
            # Check no constraints are True
            if any(group_results):
                all_constraints_satisfied = False
                for constraint, result in zip(group.constraints, group_results):
                    if result:
                        unsatisfied_constraints.append({
                            "operator": "NOT",
                            "constraint": constraint
                        })

    return all_constraints_satisfied, unsatisfied_constraints