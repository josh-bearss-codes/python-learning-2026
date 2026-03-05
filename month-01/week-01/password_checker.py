import string

def check_length(password):
    """Check password length strength"""
    length = len(password)
    if length < 10:
        return "Weak"
    elif length < 15:
        return "Medium"
    else:
        return "Strong"

def check_complexity(password):
    """Check password complexity strength"""
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in string.punctuation for char in password)
    complexity = sum([has_upper, has_lower, has_digit, has_special])
    
    if complexity == 4:
        return "Strong"
    elif complexity >= 3:
        return "Medium"
    else:
        return "Weak"

def get_strength(password):
    """Get both length and complexity strength"""
    length_strength = check_length(password)
    complexity_strength = check_complexity(password)
    return length_strength, complexity_strength

def get_feedback(password):
    """Generate feedback based on password strength"""
    if not password:  # Handle empty password
        return "Password cannot be empty."
    
    length_strength = check_length(password)
    complexity_strength = check_complexity(password)
    
    # If both are strong, no feedback needed
    if length_strength == "Strong" and complexity_strength == "Strong":
        return None
    
    # Build feedback based on what's missing
    feedback_parts = []
    
    if length_strength != "Strong":
        if len(password) < 10:
            feedback_parts.append("Add more characters (at least 10)")
        elif len(password) < 15:
            feedback_parts.append("Add more characters (at least 15 for strong password)")
    
    if complexity_strength != "Strong":
        missing_elements = []
        if not any(char.isupper() for char in password):
            missing_elements.append("uppercase letters")
        if not any(char.islower() for char in password):
            missing_elements.append("lowercase letters")
        if not any(char.isdigit() for char in password):
            missing_elements.append("digits")
        if not any(char in string.punctuation for char in password):
            missing_elements.append("special characters")
        
        if missing_elements:
            feedback_parts.append(f"Add {', '.join(missing_elements)}")
    
    return " and ".join(feedback_parts) if feedback_parts else None

def main():
    """Main function to run the password checker"""
    password = input("Enter your password: ")
    length_strength, complexity_strength = get_strength(password)
    print(f"Length Strength: {length_strength}")
    print(f"Complexity Strength: {complexity_strength}")
    feedback = get_feedback(password)
    if feedback:
        print(f"Feedback: {feedback}")

if __name__ == "__main__":
    main()
