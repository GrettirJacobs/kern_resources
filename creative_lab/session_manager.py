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
        # Initialize links file if it doesn't exist
        self.links_file = self.base_path / "links.json"
        if not self.links_file.exists():
            with open(self.links_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
    
    def save_conversation(self, model_name, content):
        """Save a conversation with an AI model"""
        conv_path = self.base_path / "conversations" / self.session_id
        print(f"Saving conversation to: {conv_path}")
        conv_path.mkdir(parents=True, exist_ok=True)
        file_path = conv_path / f"{model_name}_conversation.txt"
        print(f"Full file path: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def save_markdown_conversation(self, model_name, content, metadata=None):
        """Save a conversation in Markdown format with metadata
        
        Args:
            model_name (str): Name of the AI model
            content (str): The conversation content
            metadata (dict, optional): Additional metadata about the conversation
        """
        conv_path = self.base_path / "conversations" / self.session_id
        print(f"Saving markdown conversation to: {conv_path}")
        conv_path.mkdir(parents=True, exist_ok=True)
        
        # Prepare markdown content with metadata
        markdown_content = f"""# Conversation with {model_name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Metadata
- Session ID: {self.session_id}
- Model: {model_name}
"""
        
        # Add any additional metadata
        if metadata:
            markdown_content += "\n### Additional Metadata\n"
            for key, value in metadata.items():
                markdown_content += f"- {key}: {value}\n"
        
        # Add the main content
        markdown_content += f"\n## Content\n\n{content}\n"
        
        # Save the file
        file_path = conv_path / f"{model_name}_conversation.md"
        print(f"Full file path: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return file_path

    def save_insight(self, model_name, insight_data):
        """Save insights from an AI model"""
        insight_path = self.base_path / "insights" / self.session_id
        print(f"Saving insight to: {insight_path}")
        insight_path.mkdir(parents=True, exist_ok=True)
        
        file_path = insight_path / f"{model_name}_insight.json"
        print(f"Full file path: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(insight_data, f, indent=4)
        return file_path

    def link_conversation_to_insight(self, conversation_path, insight_path):
        """Create a link between a conversation and its insight"""
        print(f"Linking conversation to insight...")
        # Load existing links
        with open(self.links_file, "r", encoding="utf-8") as f:
            links = json.load(f)
        
        # Create new link
        link_data = {
            "session_id": self.session_id,
            "conversation": str(conversation_path),
            "insight": str(insight_path),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to links
        if self.session_id not in links:
            links[self.session_id] = []
        links[self.session_id].append(link_data)
        
        # Save updated links
        with open(self.links_file, "w", encoding="utf-8") as f:
            json.dump(links, f, indent=4)
        print(f"Link created successfully")

    def get_linked_files(self, session_id=None):
        """Retrieve linked files for a session"""
        print(f"Retrieving linked files...")
        
        # Load links file
        with open(self.links_file, "r", encoding="utf-8") as f:
            links = json.load(f)
        
        # Use provided session_id or current session
        target_session = session_id or self.session_id
        
        if target_session in links:
            print(f"Found links for session {target_session}")
            return links[target_session]
        else:
            print(f"No links found for session {target_session}")
            return []