from flask import Flask, render_template, request
from backend import sp, save_tracks, search_songs, use_preset
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
    # Get data from form
    keywords = request.form['keywords']
    genre = request.form['genre']
    length = request.form['length']

    # Process data
    keyword_list = [k.strip() for k in keywords.split(',')]
    genre_list = genre.split(",")

    try:
        # Search songs
        track_ids = search_songs(sp, seed_words=keyword_list, genres=genre_list, length=length)

        # Save playlist on Spotify
        playlist_name = "User Generated Playlist"
        save_tracks(sp, track_ids, playlist_name=playlist_name)

        return render_template ("congrats.html") #f"Playlist '{playlist_name}' created successfully with {len(track_ids)} tracks!"
    except ValueError as ve:
        return f"Error: {ve}"
    except Exception as e:
        return f"Unexpected error: {e}"

@app.route('/use_preset', methods=['POST'])
def use_presetflask():
    preset=request.form['preset']
    length=request.form['length']

    try:
        # Search preset
        use_preset(sp, preset_name=preset, json_path="presets.json", length=length, randomness=0.1)

        return render_template ("congrats.html") #f"Playlist '{playlist_name}' created successfully with {len(track_ids)} tracks!"
    except ValueError as ve:
        return f"Error: {ve}"
    except Exception as e:
        return f"Unexpected error: {e}"


if __name__ == "__main__":
    app.run(debug=True)
