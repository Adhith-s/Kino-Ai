import pickle
import os
import torch
import random

# Disable SSL verification to prevent huggingface_hub download failures in restricted networks
import httpx
orig_httpx_init = httpx.Client.__init__
def patched_httpx_init(self, *args, **kwargs):
    kwargs['verify'] = False
    orig_httpx_init(self, *args, **kwargs)
httpx.Client.__init__ = patched_httpx_init

try:
    import requests
    requests.Session.verify = False
except ImportError:
    pass

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

from sentence_transformers import SentenceTransformer, util
import ollama
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor


# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'movies_db.pkl')

# 1. Load the pre-computed database and embeddings
# 1. Load the pre-computed database and embeddings
try:
    print("========================================")
    print("BASE_DIR =", BASE_DIR)
    print("DB_PATH =", DB_PATH)
    print("Database exists =", os.path.exists(DB_PATH))

    with open(DB_PATH, "rb") as f:
        data = pickle.load(f)

    movies_df = data["movies"]
    movie_embeddings = data["embeddings"]

    print(f"[OK] Loaded {len(movies_df)} movies with embeddings.")
    print("Columns:", movies_df.columns.tolist())

    if len(movies_df) > 0:
        print("First 5 rows:")
        print(movies_df.head())

    print("========================================")

except Exception as e:
    print("========================================")
    print("DATABASE LOAD ERROR")
    print(type(e).__name__)
    print(e)
    print("========================================")

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
    """Generate a premium AI explanation. 
    Order: OpenAI (Cloud) -> Ollama (Local) -> Templates (Fallback)
    """
    prompt = f"""
    User is looking for: "{query}"
    Movie Title: "{title}"
    Movie Overview: "{overview}"
    
    Task: Write a one-sentence, very compelling 'vibe-check' explanation of why this movie matches the user's search. 
    Be cinematic and evocative. Keep it under 25 words.
    """

    # 1. Try OpenAI (Recommended for Production/Vercel)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.7
            )
            return response.choices[0].message.content.strip().strip('"')
        except Exception as e:
            print(f"OpenAI Error: {e}")

    # 2. Try Ollama (Local Development)
    try:
        # Use a client with a strict timeout to prevent hanging the whole app
        client = ollama.Client(timeout=10) 
        response = client.generate(
            model='llama3', 
            prompt=prompt,
            options={'num_predict': 50, 'temperature': 0.7}
        )
        return response['response'].strip().strip('"')
    except Exception as e:
        # 3. Fallback to Templates
        print(f"LLM Info: Using cinematic templates (Local LLM timed out or unavailable).")
        templates = [
            f"If you're craving '{query}', this cinematic gem delivers exactly that vibe and more.",
            f"A must-watch for anyone searching for '{query}' — this one hits every note perfectly.",
            f"Your search for '{query}' led straight to this masterpiece.",
            f"This film captures the essence of '{query}' in a way that will leave you breathless.",
            f"A definitive match for your interest in '{query}'.",
        ]
        return random.choice(templates)




def recommend(query: str):
    """Fast semantic search with parallel LLM explanations."""
    if movies_df is None or movie_embeddings is None:
        return [{"title": "Database Error", "poster": "", "explanation": "Run build_db.py first."}]

    try:
        query_embedding = embedding_model.encode(query, convert_to_tensor=True)
        cosine_scores = util.cos_sim(query_embedding, movie_embeddings)[0]
        top_results = torch.topk(cosine_scores, k=min(10, len(movies_df)))
    except Exception as e:
        print(f"Embedding error: {e}")
        return [{"title": "Search Error", "poster": "", "explanation": str(e)}]

    # Prepare initial results list
    results = []
    indices = top_results.indices.tolist()
    scores = top_results.values.tolist()

    # Pre-populate results with basic info
    for i in range(len(indices)):
        idx = int(indices[i])
        movie = movies_df.iloc[idx]
        results.append({
            "title": movie['title'],
            "poster": fetch_poster(movie),
            "overview": movie['overview'],
            "explanation": "",  # To be filled
            "match": round(float(scores[i]) * 100, 1),
            "genres": movie.get('genres', '') if isinstance(movie, dict) else getattr(movie, 'genres', ''),
        })

    # Parallelize LLM explanations for the TOP 1 result only to keep it extremely fast
    # (90s delay detected previously - reducing to 1 helps significantly)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            get_explanation, 
            query, 
            results[0]["title"], 
            results[0]["overview"]
        )
        
        try:
            results[0]["explanation"] = future.result()
        except Exception as e:
            print(f"Explanation error: {e}")
            results[0]["explanation"] = f"A perfect cinematic match for your interest in {query}."

    # Fill in templates for ALL other results (2-10)
    for i in range(1, len(results)):
        templates = [
            f"If you're craving '{query}', this cinematic gem delivers exactly that vibe.",
            f"A must-watch for anyone searching for '{query}'.",
            f"Your search for '{query}' led straight to this masterpiece.",
            f"Matches your craving for {query}.",
            f"Fits the {query} vibe perfectly."
        ]
        results[i]["explanation"] = random.choice(templates)

    return results



def get_popular(category: str = "all"):
    """Return popular movies."""

    print("===== get_popular() =====")

    if movies_df is None:
        print("movies_df is None")
        return []

    print("Total movies:", len(movies_df))

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

    print("Filtered movies:", len(filtered))

    if len(filtered) == 0:
        return []

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