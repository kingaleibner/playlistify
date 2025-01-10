import random
import requests
import json
import spotipy
import re
from spotipy.oauth2 import SpotifyOAuth


CLIENT_ID = 'd785b384a5664b6b86edb20004069723' 
CLIENT_SECRET = '28de0fba015f443eb62a19d998b9a6ae' 
REDIRECT_URI = 'http://localhost:3000'
SCOPE = "playlist-modify-private playlist-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))


def get_related_words(word, lang='en', min_weight=0.55):
    """
    Fetches related words for a given word from ConceptNet, excluding antonyms
    and keeping only words in the specified language.
    
    :param word: Input word (must be a string).
    :param lang: Language (default is 'en').
    :param min_weight: Minimum weight of connection to accept the word.
    :return: List of unique filtered related words.
    """
    if not isinstance(word, str):
        raise ValueError("The input 'word' must be a string.")
    
    url = f"http://api.conceptnet.io/c/{lang}/{word}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching data from ConceptNet: {response.status_code}")
        return []
    
    edges = response.json().get('edges', [])
    related_words = set()

    for edge in edges:
        # Check relationship type
        if edge['rel']['label'] in ['RelatedTo', 'Synonym']:
            weight = edge.get('weight', 0)
            if weight >= min_weight:
                related_word = edge['end']['label'] if edge['start']['label'].lower() == word.lower() else edge['start']['label']
                related_word_id = edge['end']['@id'] if edge['start']['label'].lower() == word.lower() else edge['start']['@id']
                
                # Ensure word is in the desired language
                if related_word_id.startswith(f"/c/{lang}/"):
                    # Add only single words in the Latin alphabet
                    if re.match(r'^[a-zA-Z]+$', related_word):
                        related_words.add(related_word.lower())
        
        # Remove antonyms
        if edge['rel']['label'] == 'Antonym':
            antonym = edge['end']['label'] if edge['start']['label'].lower() == word.lower() else edge['start']['label']
            if re.match(r'^[a-zA-Z]+$', antonym):
                related_words.discard(antonym.lower())

    # Ensure the input word is included if it's valid
    if re.match(r'^[a-zA-Z]+$', word):
        related_words.add(word.lower())

    print(f"Filtered related words for '{word}': {related_words}")
    return sorted(related_words)


def get_similar_genres(input_genre=None, genre_file_path="genres.txt"):
    """
    Matches the user-provided genre with similar genres available in Spotify's API.
    Uses ConceptNet to find synonyms and filters against the Spotify genres list.
    If no genre is provided, it defaults to no genre restrictions.
    
    :param input_genre: The genre entered by the user, or None for no genre restriction.
    :param genre_file_path: Path to the file containing available Spotify genres.
    :return: List of similar genres or an empty list if no genre is provided.
    """
    # Read available genres from the file
    with open(genre_file_path, 'r') as file:
        available_genres = {line.strip().lower() for line in file}

    print(available_genres)

    # If no genre is provided, return an empty list (no restriction)
    if not input_genre:
        return []

    input_genre = input_genre.strip().lower()  # Normalize the input genre
    print(input_genre)
    
    # Get related genres using the existing function
    related_genres = get_related_words(input_genre)
    
    # Split the input genre into words (in case it's a multi-word genre)
    input_genre_words = input_genre.split()

    # Combine related genres and the input genre words
    related_genres = related_genres + input_genre_words

    # Deduplicate by converting to a set and then back to a sorted list
    related_genres = sorted(set(related_genres))

    print(related_genres)

    # Filter to include only genres available in Spotify
    filtered_genres = [genre for genre in related_genres if genre in available_genres]

    # Add the input genre itself if it is valid and not already in filtered_genres
    if input_genre in available_genres and input_genre not in filtered_genres:
        filtered_genres.append(input_genre)

    print(filtered_genres)

    # If no similar genres are found, return the input genre itself if valid
    if not filtered_genres:
        return []
    return sorted(filtered_genres)


def search_songs(sp, seed_words, genres=None, length=None, randomness=0.1):
    """
    Searches for tracks on Spotify based on keywords and genres, ensuring uniqueness,
    slight randomness, and a minimum playlist length. Filters tracks with popularity > 30.
    Includes a timeout to prevent infinite search loops.

    :param sp: Spotify API connection.
    :param seed_words: List of keywords for search.
    :param genres: List of genres to include in the search. If None, no genre restriction.
    :param length: Number of tracks in the results. Defaults to 20 if None.
    :param randomness: Chance (from 0 to 1) for a track to be skipped.
    :return: List of unique track IDs.
    """
    if not length: 
        length = 20
    else:
        length = int(length)

    # Generate all related keywords
    all_keywords = list(set(seed_words))  # Convert to list for indexing
    for word in seed_words:
        related_words = get_related_words(word)
        all_keywords.extend(related_words)
    all_keywords = list(set(all_keywords))  # Remove duplicates
    print(f"[INFO] Extended and filtered keywords: {all_keywords}")

    # Generate all related genres
    all_genres = set()
    if genres:
        for genre in genres:
            related_genres = get_similar_genres(genre)
            all_genres.update(related_genres)

    print(f"[INFO] Extended and filtered genres: {all_genres}")

    found_tracks = {}
    keyword_usage = {keyword: 0 for keyword in all_keywords}  # Track how often each keyword is used
    max_attempts = 2 * length
    attempts = 0  # Counter for search attempts

    while len(found_tracks) < length:
        if attempts >= max_attempts:
            print(f"[TIMEOUT] Maximum search attempts ({max_attempts}) reached. Returning partial results.")
            break

        # Increment the attempts counter
        attempts += 1

        # Randomly pick a keyword for this iteration, biasing towards less-used keywords
        word = random.choices(
            population=all_keywords,
            weights=[1 / (1 + keyword_usage[w]) for w in all_keywords],  # Less-used keywords get higher weight
            k=1
        )[0]
        keyword_usage[word] += 1  # Increment usage for the selected keyword

        # Build the query string
        query = f"{word}"
        if genres:
            random_genre = random.choice(list(all_genres)) if all_genres else None
            if random_genre:
                query += f" genre:{random_genre}"
        print(f"[INFO] Searching for tracks with query: {query}")
        try:
            results = sp.search(q=query, type='track', limit=10)
            print(f"[INFO] Found {len(results['tracks']['items'])} tracks for query: {query}")
            for track in results['tracks']['items']:
                track_id = track['id']
                popularity = track['popularity'] / 100  # Convert to 0-1 range
                # Add randomization to skip some tracks
                if (track_id not in found_tracks and popularity > 0.3
                        and random.random() > randomness):
                    found_tracks[track_id] = {
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'popularity': popularity
                    }
                    print(f"[TRACK FOUND] Track '{track['name']}' by {track['artists'][0]['name']} added.")
        except Exception as e:
            print(f"[ERROR] Error during search for word '{word}': {e}")

        # Stop searching if we've already found the required number of tracks
        if len(found_tracks) >= length:
            print("[INFO] Required number of tracks found. Stopping search.")
            break

    # If the number of tracks found is less than length, return only the found tracks
    unique_tracks = list(found_tracks.items())[:length]  # Limit the number of tracks to length
    print(f"[SUMMARY] Found {len(unique_tracks)} unique tracks out of {length} requested.")

    # Return only track IDs for playlist creation
    return [track_id for track_id, _ in unique_tracks]


def save_tracks(sp, track_ids, playlist_name="Randomized Playlist"):
    """
    Saves unique tracks to a Spotify playlist.
    
    :param sp: Spotify API connection.
    :param track_ids: List of unique track IDs.
    :param playlist_name: Name of the new playlist.
    """
    if not track_ids:
        print("No tracks to save. Operation aborted.")
        return
    
    try:
        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
        playlist_id = playlist['id']
        print(f"Created playlist '{playlist_name}' (ID: {playlist_id})")

        # Add tracks to the playlist
        sp.playlist_add_items(playlist_id, track_ids)
        print(f"Added {len(track_ids)} tracks to playlist '{playlist_name}'.")
    except Exception as e:
        print(f"Error saving playlist: {e}")


def load_presets(json_path):
    """
    Loads presets from a JSON file.
    
    :param json_path: Path to the JSON file containing presets.
    :return: Dictionary of presets.
    """
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        return data.get('presets', {})
    except Exception as e:
        print(f"Error loading presets: {e}")
        return {}

def use_preset(sp, preset_name, json_path="presets.json", length=20, randomness=0.1):
    """
    Uses a preset to search for songs and create a playlist.
    
    :param sp: Spotify API connection.
    :param preset_name: Name of the preset to use.
    :param json_path: Path to the JSON file containing presets.
    :param min_length: Minimum number of tracks to include in the playlist.
    :param randomness: Chance (from 0 to 1) for a track to be skipped.
    """
    presets = load_presets(json_path)
    preset = presets.get(preset_name)
    print(preset)
    
    if not preset:
        print(f"Preset '{preset_name}' not found. Available presets: {', '.join(presets.keys())}")
        return
    
    print(f"Using preset: {preset['name']}")
    
    # Extract seed words and genres from the preset
    seed_words = preset.get('seed_words', [])
    genres = preset.get('genres', [])
    
    # Search for songs
    track_ids = search_songs(sp, seed_words, genres=genres, length=length, randomness=randomness)
    
    # Save the tracks to a playlist
    save_tracks(sp, track_ids, playlist_name=preset['name'])
