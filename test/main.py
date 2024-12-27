from flask import Flask, render_template, request
from backend import get_related_words, get_similar_genres, sp, save_tracks, search_songs
app = Flask(__name__)

@app.route("/home")


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/preset")
def preset():
    return render_template("preset.html") 

@app.route("/create")
def create():
    return render_template("create.html") 

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # Pobierz dane z formularza
    keywords = request.form['keywords']
    genre = request.form['genre']
    length = request.form['length']

    # Przetwórz dane
    keyword_list = [k.strip() for k in keywords.split(',')]
    genres = get_similar_genres(genre) if genre else None
    lengthin = int(length)

    try:
        # Wyszukaj utwory
        track_ids = search_songs(sp, seed_words=keyword_list, genres=genres, length=lengthin)

        # Zapisz playlistę na Spotify
        playlist_name = "User Generated Playlist"
        save_tracks(sp, track_ids, playlist_name=playlist_name)

        return render_template ("congrats.html") #f"Playlist '{playlist_name}' created successfully with {len(track_ids)} tracks!"
    except ValueError as ve:
        return f"Error: {ve}"
    except Exception as e:
        return f"Unexpected error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
