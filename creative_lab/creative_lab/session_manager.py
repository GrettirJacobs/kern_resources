from datetime import datetime
from pathlib import Path

class CreativeSession:
    def __init__(self, base_path="creative_lab"):
        self.base_path = Path(base_path)
        self.session_id = None
    
    def start_new_session(self, name):
        """Start a new creative session with the given name"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.session_id = f"{name}_{timestamp}"
        return self.session_id
    
    def save_conversation(self, model_name, content):
        """Save a conversation with an AI model"""
        if not self.session_id:
            self.start_new_session("default")
            
        conv_path = self.base_path / "conversations" / self.session_id
        conv_path.mkdir(parents=True, exist_ok=True)
        
        file_path = conv_path / f"{model_name}_{datetime.now().strftime('%H%M%S')}.txt"
        file_path.write_text(content)
        return str(file_path)