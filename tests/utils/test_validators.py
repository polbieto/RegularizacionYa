import pytest
from chatregularizacion.utils.validators import check_email

def test_check_email_valid():
    # Valid email syntax and domain
    result = check_email("test@google.com")
    assert result == "test@google.com"

def test_check_email_invalid_syntax():
    # Invalid email syntax
    result = check_email("invalid-email")
    assert result is None

def test_check_email_invalid_deliverability():
    # Invalid domain (does not exist)
    result = check_email("test@thisdomaindoesnotexist.invalid")
    assert result is None
