import pickle
import os
import torch
import random
from sentence_transformers import SentenceTransformer, util
import ollama

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'movies_db.pkl')

# 1. Load the pre-computed database and embeddings
try:
    with open(DB_PATH, 'rb') as f:
        data = pickle.load(f)
        movies_df = data['movies']
        movie_embeddings = data['embeddings']
    print(f"[OK] Loaded {len(movies_df)} movies with embeddings.")
except FileNotFoundError:
    print(f"Error: {DB_PATH} not found. Please run build_db.py first.")
    movies_df = None
    movie_embeddings = None

# 2. Load the semantic search model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


# TMDB Poster base URL
TMDB_POSTER_BASE = "https://image.tmdb.org/t/p/w500"


def fetch_poster(movie):
    """Get poster URL from movie's poster_path field."""
    poster_path = movie.get('poster_path', '') if isinstance(movie, dict) else getattr(movie, 'poster_path', '')
    if poster_path and str(poster_path) != 'nan':
        return f"{TMDB_POSTER_BASE}{poster_path}"
    title = movie.get('title', '') if isinstance(movie, dict) else getattr(movie, 'title', 'Movie')
    return f"https://placehold.co/500x750/111111/DC2626?text={title.replace(' ', '+')}&font=raleway"


def get_explanation(query, title, overview):
    """Generate a premium AI explanation. Falls back to templates if LLM is unavailable."""
    try:
        # Check if Ollama is likely available (local) or if we are in cloud
        prompt = f"""
        User is looking for: "{query}"
        Movie Title: "{title}"
        Movie Overview: "{overview}"
        
        Task: Write a one-sentence, very compelling 'vibe-check' explanation of why this movie matches the user's search. 
        Be cinematic and evocative. Keep it under 25 words.
        """
        
        response = ollama.generate(model='llama3', prompt=prompt)
        return response['response'].strip().strip('"')
    except Exception as e:
        # This is expected in most cloud deployments unless Ollama is specifically hosted
        print(f"LLM Info: Using cinematic templates (Local LLM not detected).")
        templates = [
            f"If you're craving '{query}', this cinematic gem delivers exactly that vibe and more.",
            f"A must-watch for anyone searching for '{query}' — this one hits every note perfectly.",
            f"Your search for '{query}' led straight to this masterpiece.",
            f"This film captures the essence of '{query}' in a way that will leave you breathless.",
            f"A definitive match for your interest in '{query}'.",
        ]
        return random.choice(templates)




def recommend(query: str):
    """Fast semantic search — no LLM calls."""
    if movies_df is None or movie_embeddings is None:
        return [{"title": "Database Error", "poster": "", "explanation": "Run build_db.py first."}]

    try:
        query_embedding = embedding_model.encode(query, convert_to_tensor=True)
        cosine_scores = util.cos_sim(query_embedding, movie_embeddings)[0]
        top_results = torch.topk(cosine_scores, k=min(10, len(movies_df)))
    except Exception as e:
        print(f"Embedding error: {e}")
        return [{"title": "Search Error", "poster": "", "explanation": str(e)}]

    results = []
    for i, (score, idx) in enumerate(zip(top_results.values, top_results.indices)):
        movie = movies_df.iloc[int(idx)]
        title = movie['title']
        overview = movie['overview']
        similarity = round(float(score) * 100, 1)

        # Only use Ollama for top 3 results to keep performance snappy
        if i < 3:
            explanation = get_explanation(query, title, overview)
        else:
            # Quick fallback for remaining results
            templates = [
                f"Matches your craving for {query}.",
                f"A great follow-up for {query} fans.",
                f"Fits the {query} vibe perfectly."
            ]
            explanation = random.choice(templates)

        results.append({
            "title": title,
            "poster": fetch_poster(movie),
            "overview": overview,
            "explanation": explanation,
            "match": similarity,
            "genres": movie.get('genres', '') if isinstance(movie, dict) else getattr(movie, 'genres', ''),
        })

    return results



def get_popular(category: str = "all"):
    """Return popular movies."""
    if movies_df is None:
        return []

    if category == "movies":
        action_genres = ['Action', 'Crime', 'Thriller', 'Sci-Fi']
        mask = movies_df['genres'].apply(lambda g: any(ag in str(g) for ag in action_genres))
        filtered = movies_df[mask]
    elif category == "series":
        drama_genres = ['Drama', 'Romance', 'Biography', 'History']
        mask = movies_df['genres'].apply(lambda g: any(dg in str(g) for dg in drama_genres))
        filtered = movies_df[mask]
    else:
        filtered = movies_df

    sampled = filtered.sample(n=min(10, len(filtered)))

    results = []
    for _, movie in sampled.iterrows():
        results.append({
            "title": movie['title'],
            "poster": fetch_poster(movie),
            "overview": movie['overview'],
            "explanation": "",
            "match": 0,
            "genres": movie.get('genres', '') if isinstance(movie, dict) else getattr(movie, 'genres', ''),
        })

    return results


def get_by_genre(genre: str):
    """Return movies matching a genre keyword."""
    if movies_df is None:
        return []

    genre_lower = genre.lower()
    mask = movies_df['genres'].apply(lambda g: genre_lower in str(g).lower())
    matched = movies_df[mask]

    if matched.empty:
        return recommend(genre)

    sampled = matched.sample(n=min(10, len(matched)))
    results = []
    for _, movie in sampled.iterrows():
        results.append({
            "title": movie['title'],
            "poster": fetch_poster(movie),
            "overview": movie['overview'],
            "explanation": "",
            "match": 0,
            "genres": movie.get('genres', '') if isinstance(movie, dict) else getattr(movie, 'genres', ''),
        })

    return results