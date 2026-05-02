import pickle
import requests

# ==============================
# LOAD DATA
# ==============================
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ==============================
# RECOMMENDATION FUNCTION
# ==============================
def recommend(movie):
    movie = movie.lower()

    # Check if movie exists
    if movie not in movies['title'].str.lower().values:
        return ["Movie not found"]

    # Get index of the movie
    index = movies[movies['title'].str.lower() == movie].index[0]

    # Get similarity scores
    distances = similarity[index]

    # Get top 5 similar movies
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []

    for i in movie_list:
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies


# ==============================
# FETCH POSTER (OMDB API)
# ==============================
API_KEY = "YOUR_OMDB_API_KEY"

def fetch_poster(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={API_KEY}"
        data = requests.get(url).json()

        if data.get("Poster") and data["Poster"] != "N/A":
            return data["Poster"]
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"

    except:
        return "https://via.placeholder.com/300x450?text=Error"


# ==============================
# COMBINED FUNCTION
# ==============================
def recommend_with_posters(movie):
    names = recommend(movie)
    posters = []

    for name in names:
        posters.append(fetch_poster(name))

    return names, posters