# Startup-Intelligence-Evaluator

**An AI-powered startup research and evaluation platform that helps entrepreneurs analyze startup ideas, understand market opportunities, evaluate competitors, and explore financial feasibility.**

## 📌 Overview

Startup Intelligence Evaluator is an AI-powered platform designed to help entrepreneurs and aspiring founders make informed business decisions before launching a startup.

The platform uses multiple specialized AI research agents to analyze startup ideas from different perspectives, including market research, competitor analysis, instant idea validation, and financial evaluation.

It integrates Gemini API for AI-powered analysis, Tavily API for web research, and SQLite for storing application data.

## ✨ Key Features

- **AI Startup Analysis:** Evaluate startup ideas using AI-powered research and analysis.
- **Multi-Agent Research System:** Uses seven specialized research agents coordinated through asynchronous execution.
- **Market Research:** Explore market opportunities, industry trends, and target audiences.
- **Competitor Analysis:** Research competitors and understand the competitive landscape.
- **Instant Idea Validation:** Analyze startup concepts and identify potential opportunities and challenges.
- **Financial Simulator:** Explore financial assumptions and potential business scenarios.
- **Past Reports:** Access previously generated startup analysis reports.
- **Interactive Dashboard:** View research insights and analysis through a centralized interface.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| AI Integration | Gemini API |
| Web Research | Tavily API |
| Database | SQLite |
| Agent Orchestration | Python Asyncio |
| Server | Uvicorn |

## 🏗️ System Architecture

The application follows an AI-powered multi-agent workflow.

1. **User Input:** User submits a startup idea through the dashboard.
2. **Backend Processing:** FastAPI receives and processes the request.
3. **AI Integration:** Gemini API supports AI-powered reasoning and analysis.
4. **Web Research:** Tavily API retrieves relevant online research information.
5. **Multi-Agent Execution:** Seven specialized research agents perform their respective analysis tasks using asynchronous execution.
6. **Data Storage:** SQLite stores application data and reports.
7. **Results:** The dashboard presents the generated insights and reports.

## 📊 Dashboard Modules

The application includes the following modules:

- AI Analysis
- Market Research
- Competition Analysis
- Instant Validation
- Financial Simulator
- Past Reports

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kanix0067/Startup-Intelligence-Evaluator.git
```

### 2. Navigate to the Project

```bash
cd Startup-Intelligence-Evaluator
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure API Keys

Create a `.env` file in the project root and configure the API credentials using the environment variable names expected by the application.

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Obtain API keys from:

- [Google AI Studio](https://aistudio.google.com/)
- [Tavily](https://tavily.com/)

**Important:** Never upload your `.env` file or expose API credentials publicly.

### 7. Run the Application

Start the FastAPI server using the actual Python module containing your FastAPI application.

```bash
uvicorn main:app --reload
```

Replace `main` with the correct module name if your application uses a different entry-point file.

Access the API documentation at:

```text
http://127.0.0.1:8000/docs
```

## 📁 Project Highlights

- AI-powered startup evaluation.
- Multiple specialized research agents.
- Asynchronous agent execution.
- Integration with external AI and web-search APIs.
- Database-backed report management.
- Interactive startup research dashboard.

## 🔮 Future Enhancements

- More advanced startup evaluation models.
- Improved market prediction capabilities.
- Additional financial analysis methods.
- Enhanced visualization and reporting.
- More specialized AI research agents.

## 👨‍💻 Developer

**KANIGA K**

- GitHub: [@kanix0067](https://github.com/kanix0067)
- Project Repository: [Startup Intelligence Evaluator](https://github.com/kanix0067/Startup-Intelligence-Evaluator)

---

⭐ If you find this project interesting, consider giving the repository a star!

