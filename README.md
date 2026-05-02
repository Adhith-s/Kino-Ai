# 🎬 KINO AI: Premium Movie Recommender

![Kino AI Banner](https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=2059&auto=format&fit=crop)

KINO AI is a state-of-the-art movie discovery engine that leverages **Semantic Search** and **Local LLMs** (Ollama) to provide a premium, cinematic experience. Instead of just searching by title, you can describe a "vibe," a plot point, or a specific mood, and KINO AI will find the perfect match.

---

## 💎 Features

- **🧠 Semantic Discovery**: Powered by `sentence-transformers` (all-MiniLM-L6-v2), understanding the context of your request beyond simple keywords.
- **🤖 AI Rationales**: Integrates with **Ollama (Llama 3/Mistral)** to generate custom, Netflix-style "Why you'll love this" explanations for every recommendation.
- **🍿 Cinematic UI**: A high-end, responsive interface built with Tailwind CSS, featuring glassmorphism, fluid animations, and a dynamic hero section.
- **⚡ Fast & Local**: All AI processing happens on your local machine, ensuring privacy and speed.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS.
- **Backend**: Python, FastAPI.
- **AI/ML**: 
  - `Sentence-Transformers` for vector embeddings.
  - `PyTorch` for similarity calculations.
  - `Ollama` for dynamic LLM content generation.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- [Ollama](https://ollama.com/) installed and running.
- Pull the preferred model: `ollama pull llama3`

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize the AI Database
Before running the app, generate the vector embeddings for the movie dataset:
```bash
python generate_embeddings.py
```

### 4. Start the Application
**Backend:**
```bash
uvicorn main:app --reload
```

**Frontend:**
Simply open `frontend/index.html` in your browser or use a Live Server.

---

## 📁 Project Structure

```text
├── backend/
│   ├── main.py                # FastAPI Entry Point
│   ├── recommender.py         # AI Logic & Ollama Integration
│   ├── generate_embeddings.py # Data Pre-processing Script
│   └── requirements.txt       # Dependencies
├── dataset/
│   └── tmdb_5000_movies.csv   # Movie Dataset
└── frontend/
    ├── index.html             # UI Structure
    ├── css/style.css          # Premium Styles
    └── js/script.js           # Frontend Interaction
```

---

## 🎨 Aesthetic Design Principles
KINO AI follows a **Dark Cinematic** design language:
- **Primary Color**: `#DC2626` (Cinema Red)
- **Background**: Deep Black `#050505` with subtle gradients.
- **Typography**: `Outfit` for a modern, clean look.
- **Interactions**: Smooth hover states, lazy-loaded animations, and backdrop-blur effects.

---

Developed with ❤️ by Antigravity.
