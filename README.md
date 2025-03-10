MIT License

Copyright (c) 2023 Erik Jacobs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# Creative Lab System

An AI-powered creative laboratory system for managing project conversations, insights, and knowledge synthesis. Part of the Kern Resources project.

## 🌟 Features

- **Conversation Management**: Track and organize project-related discussions
- **Insight Generation**: AI-powered analysis of conversations and content
- **Project Memory**: Intelligent storage and retrieval of project knowledge
- **Automated Linking**: Smart connections between related content
- **Session Management**: Structured creative sessions with AI assistance

## 🏗️ Project Structure

```
creative_lab/
├── conversations/       # Stored conversation data
├── insights/           # Generated AI insights
├── project_memory/     # Memory system implementation
├── session_manager.py  # Session management logic
├── links.json         # Content relationship mapping
└── tests/             # Test suite
    ├── test_insights.py
    ├── test_linking.py
    ├── test_markdown.py
    ├── test_retrieval.py
    └── test_session.py
```

## 🚀 Getting Started

1. **Prerequisites**
   - Python 3.8+
   - Dependencies listed in requirements.txt

2. **Installation**
   ```bash
   git clone https://github.com/GrettirJacobs/kern_resources.git
   cd kern_resources/creative_lab
   pip install -r requirements.txt
   ```

3. **Running Tests**
   ```bash
   pytest
   ```

## 💡 Usage

1. **Start a Creative Session**
   ```python
   from session_manager import CreativeSession
   
   session = CreativeSession()
   session.start_new_session("Project Brainstorming")
   ```

2. **Generate Insights**
   ```python
   insights = session.generate_insights()
   session.save_insights(insights)
   ```

3. **Link Related Content**
   ```python
   session.link_content("conversation_id", "insight_id")
   ```

## 🔧 Development

- Run tests: `pytest`
- Check code style: `flake8`
- Generate documentation: `pdoc3 --html .`

## 📚 Documentation

- Session Management: Handles creative sessions and conversation flow
- Insight Generation: AI-powered analysis and synthesis
- Memory System: Long-term storage and retrieval
- Content Linking: Relationship mapping between different content types

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [Kern Resources](https://github.com/GrettirJacobs/kern_resources) - Main project repository
