from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from recommender import recommend, get_popular, get_by_genre
import os

app = FastAPI(title="Kino AI API")

# Get the base directory (where main.py is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Serve posters directory
posters_path = os.path.join(PROJECT_ROOT, "posters")
if os.path.exists(posters_path):
    app.mount("/posters", StaticFiles(directory=posters_path), name="posters")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/recommend")
def get_recommend(query: str):
    try:
        return recommend(query)
    except Exception as e:
        return {"error": str(e)}

@app.get("/popular")
def get_popular_movies(category: str = "all"):
    """Get popular movies, optionally filtered by category."""
    try:
        return get_popular(category)
    except Exception as e:
        return {"error": str(e)}

@app.get("/genre")
def get_genre_movies(genre: str):
    """Get movies by genre/vibe."""
    try:
        return get_by_genre(genre)
    except Exception as e:
        return {"error": str(e)}

# Serve frontend directory (MUST be last - catches all remaining routes)
frontend_path = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")