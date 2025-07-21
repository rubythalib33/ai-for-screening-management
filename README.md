# AI for Talent Acquisition

This project is an AI-powered application for enhancing the recruitment process. It provides intelligent **CV Scoring and Ranking** and **Interview Scoring and Ranking** to help HR teams prioritize top candidates efficiently.

---

## ✨ Features

- ✅ **CV Scoring and Ranking**  
  Automatically evaluates and ranks candidates based on their submitted CVs.

- ✅ **Interview Scoring and Ranking**  
  Assists interviewers in evaluating and ranking candidates after interviews using AI insights.

---

## ⚙️ Tech Stack

- [Streamlit](https://streamlit.io) — for building the interactive web UI  
- [OpenAI API](https://openai.com) — for powering the AI logic and scoring algorithms  
- [Docker Compose](https://docs.docker.com/compose/) — for containerized deployment

---

## 🛠️ Installation

### Prerequisites

- Docker installed on your machine
- Docker Compose installed

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-talent-acquisition.git
cd ai-talent-acquisition
````

### 2. Set up environment variables

Create a `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key
```

### 3. Build and start the application

```bash
docker-compose up --build
```

---

## 🚀 How to Run

Once the container is up and running, open your browser and go to:

```
http://localhost:8501
```

You’ll see the AI Talent Acquisition dashboard where you can begin uploading CVs and scoring interviews.

---

## 👤 Author

**Ruby Abdullah**
CEO of [rubythalib.ai](https://rubythalib.ai)

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
