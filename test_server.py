import pytest
from server import Processor

def test_process_login_info_valid():
    processor = Processor()
    login_info = "username"
    name = processor.process_login_info(login_info)
    assert name == "username"

def test_process_login_info_invalid():
    processor = Processor()
    with pytest.raises(ValueError, match="Invalid login information format"):
        processor.process_login_info("invalid format")

def test_process_message_valid():
    processor = Processor()
    data = "message|user|sender"
    mes, user, sender = processor.process_message(data)
    assert mes == "message"
    assert user == "user"
    assert sender == "sender"

def test_process_message_invalid():
    processor = Processor()
    with pytest.raises(ValueError, match="Invalid message format"):
        processor.process_message("invalidformat")

def test_send_message_failure():
    processor = Processor()
    result = processor.send_message("Hello", "nonexistent_user")
    assert result is False
