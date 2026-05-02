import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle
import os

print("Loading dataset...")
# Load TMDB dataset
movies_path = '../dataset/tmdb_5000_movies.csv'
if not os.path.exists(movies_path):
    print(f"Error: Dataset not found at {movies_path}")
    exit(1)

movies_df = pd.read_csv(movies_path)

# Drop missing overviews and fill missing genres
movies_df['overview'] = movies_df['overview'].fillna('')
movies_df['genres'] = movies_df['genres'].fillna('')

# Combine overview and genres for semantic search
movies_df['search_text'] = movies_df['title'] + " " + movies_df['overview'] + " " + movies_df['genres']

print("Loading Sentence Transformer Model (all-MiniLM-L6-v2)...")
# Download/Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Generating embeddings (this may take a minute depending on your CPU)...")
# Encode the search text into vectors
embeddings = model.encode(movies_df['search_text'].tolist(), convert_to_tensor=True)

# Keep only the columns we need to save space
movies_db = movies_df[['id', 'title', 'overview']].copy()

print("Saving embeddings to movies_db.pkl...")
# Save both the dataframe and the embeddings to a single pickle file
with open('movies_db.pkl', 'wb') as f:
    pickle.dump({'movies': movies_db, 'embeddings': embeddings}, f)

print("Done! You can now start the FastAPI server.")
