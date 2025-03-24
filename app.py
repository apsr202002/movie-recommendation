import streamlit as st
import pickle
import pandas as pd
import requests

# Load the movie data and similarity matrix
movies = pd.read_csv("movies-2.csv")
similarity = pickle.load(open("similarity.pkl", "rb"))

# TMDb API key (replace with your actual key)
TMDB_API_KEY = "73d16a0a2c888499635400ac7de4b06b"  # Replace with your key

def fetch_movie_details(movie_id):
    """Fetch movie details (poster, overview, rating, release date) using TMDb API"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    data = response.json()

    poster_path = data.get("poster_path", None)
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"

    return {
        "poster": poster_url,
        "overview": data.get("overview", "No overview available."),
        "rating": data.get("vote_average", "N/A"),
        "release_date": data.get("release_date", "N/A")
    }

def recommend(movie):
    """Recommend similar movies"""
    try:
        index = movies[movies['title'] == movie].index[0]  # Get index of selected movie
    except IndexError:
        return [], [], [], [], []  # Return empty lists if movie not found

    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_posters = []
    overviews = []
    ratings = []
    release_dates = []

    for i in movie_list:
        movie_data = movies.iloc[i[0]]
        movie_id = movie_data["id"]  # Ensure this column exists in movies-2.csv

        details = fetch_movie_details(movie_id)

        recommended_movies.append(movie_data["title"])
        recommended_posters.append(details["poster"])
        overviews.append(details["overview"])
        ratings.append(details["rating"])
        release_dates.append(details["release_date"])
    
    return recommended_movies, recommended_posters, overviews, ratings, release_dates

# Streamlit UI
st.title("🎬 Movie Recommendation System")
st.write("Find similar movies to your favorites!")

selected_movie = st.selectbox("Select a movie", movies['title'].values)

if st.button("Recommend"):
    names, posters, overviews, ratings, release_dates = recommend(selected_movie)

    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], use_container_width=True)  # FIXED WARNING
                st.markdown(f"**{names[i]}**")
                st.markdown(f"⭐ {ratings[i]} | 📅 {release_dates[i]}")
                st.caption(overviews[i][:100] + "...")
    else:
        st.error("No recommendations found. Try another movie.")
