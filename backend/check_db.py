import pickle
import pandas as pd

try:
    with open('movies_db.pkl', 'rb') as f:
        data = pickle.load(f)
        movies_df = data['movies']
        movie_embeddings = data['embeddings']
        print(f"Loaded {len(movies_df)} movies and {len(movie_embeddings)} embeddings.")
        print("First 5 movies:")
        print(movies_df.head())
except Exception as e:
    print(f"Error: {e}")
