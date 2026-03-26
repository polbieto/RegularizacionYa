from email_validator import validate_email, EmailNotValidError

def check_email(email: str):
    try:
        # Check syntax and deliverability
        email_info = validate_email(email, check_deliverability=True)
        
        # Returns the normalized form (e.g., lowercase domain)
        return email_info.normalized
    except EmailNotValidError as e:
        print(f"Invalid email: {e}")
        return None
