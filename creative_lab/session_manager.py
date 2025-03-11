from datetime import datetime
from pathlib import Path
import os
import json

class CreativeSession:
    def __init__(self, base_path=None):
        if base_path is None:
            base_path = Path(os.path.dirname(os.path.abspath(__file__)))
        self.base_path = Path(base_path)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M")
        self.links_file = self.base_path / "links.json"
        
        # Ensure base directories exist
        (self.base_path / "conversations").mkdir(parents=True, exist_ok=True)
        (self.base_path / "insights").mkdir(parents=True, exist_ok=True)
        
        # Initialize links file if it doesn't exist
        if not self.links_file.exists():
            with open(self.links_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    def save_conversation(self, model_name, content):
        """Save a conversation with an AI model"""
        # Validate model_name
        if model_name is None:
            raise TypeError("model_name must not be None")
        if not isinstance(model_name, str):
            raise TypeError("model_name must be strings")
        if not model_name.strip():
            raise ValueError("model_name cannot be empty")

        # Validate content
        if content is None:
            raise TypeError("content must not be None")
        if not isinstance(content, str):
            raise TypeError("content must be strings")

        # Create conversation directory and save file
        conv_path = self.base_path / "conversations" / self.session_id
        conv_path.mkdir(parents=True, exist_ok=True)
        file_path = conv_path / f"{model_name}_conversation.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def save_insight(self, model_name, insight_data):
        """Save insights from an AI model"""
        # Validate model_name
        if model_name is None:
            raise TypeError("model_name must not be None")
        if not isinstance(model_name, str):
            raise TypeError("model_name must be a string")

        # Validate insight_data
        if insight_data is None:
            raise TypeError("insight_data must not be None")
        if not isinstance(insight_data, dict):
            raise TypeError("insight_data must be a dictionary")

        # Create insight directory and save file
        insight_path = self.base_path / "insights" / self.session_id
        insight_path.mkdir(parents=True, exist_ok=True)
        file_path = insight_path / f"{model_name}_insight.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(insight_data, f, indent=4)
        return file_path

    def link_conversation_to_insight(self, conv_path, insight_path):
        """Create a link between a conversation and its insight"""
        conv_path = Path(conv_path)
        insight_path = Path(insight_path)
        
        if not conv_path.exists() or not insight_path.exists():
            raise FileNotFoundError("Both conversation and insight files must exist")

        with open(self.links_file, "r", encoding="utf-8") as f:
            links = json.load(f)
        
        link_data = {
            "session_id": self.session_id,
            "conversation": str(conv_path),
            "insight": str(insight_path),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.session_id not in links:
            links[self.session_id] = []
        links[self.session_id].append(link_data)
        
        with open(self.links_file, "w", encoding="utf-8") as f:
            json.dump(links, f, indent=4)

    def get_linked_files(self, session_id=None):
        """Retrieve linked files for a session"""
        with open(self.links_file, "r", encoding="utf-8") as f:
            links = json.load(f)
        return links.get(session_id or self.session_id, [])














