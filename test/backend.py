import random
import requests
import spotipy
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


def get_related_words(word, lang='en', min_weight=0.4):
    """
    Fetches related words for a given word from ConceptNet, excluding antonyms.
    
    :param word: Input word.
    :param lang: Language (default is 'en').
    :param min_weight: Minimum weight of connection to accept the word.
    :return: List of filtered related words.
    """
    url = f"http://api.conceptnet.io/c/{lang}/{word}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching data from ConceptNet: {response.status_code}")
        return []
    
    edges = response.json().get('edges', [])
    related_words = set()

    for edge in edges:
        # Keep only Synonym and RelatedTo relationships
        if edge['rel']['label'] in ['RelatedTo', 'Synonym']:
            weight = edge.get('weight', 0)
            if weight >= min_weight:
                related_word = edge['end']['label'] if edge['start']['label'].lower() == word.lower() else edge['start']['label']
                related_words.add(related_word.lower())
        
        # Remove Antonym relationships
        if edge['rel']['label'] == 'Antonym':
            antonym = edge['end']['label'] if edge['start']['label'].lower() == word.lower() else edge['start']['label']
            related_words.discard(antonym.lower())

    return list(related_words)


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

    # If no genre is provided, return an empty list (no restriction)
    if not input_genre:
        return []

    input_genre = input_genre.strip().lower()  # Normalize the input genre
    related_genres = get_related_words(input_genre)
    related_genres.append(input_genre)  # Include the input genre itself

    # Filter to include only genres available in Spotify
    filtered_genres = [genre for genre in related_genres if genre in available_genres]

    # If no genres are found and the input genre is not valid, raise an error
    if not filtered_genres and input_genre not in available_genres:
        raise ValueError(f"The genre '{input_genre}' is not available on Spotify.")

    # If no similar genres are found, return the input genre itself if valid
    if not filtered_genres:
        return [input_genre]

    return filtered_genres


def search_songs(sp, seed_words, genres=None, length=20, randomness=0.1):
    """
    Searches for tracks on Spotify based on keywords and genres, ensuring uniqueness,
    slight randomness, and a minimum playlist length. Filters tracks with popularity > 50.
    
    :param sp: Spotify API connection.
    :param seed_words: List of keywords for search.
    :param genres: List of genres to include in the search. If None, no genre restriction.
    :param length: Minimum number of tracks in the results.
    :param randomness: Chance (from 0 to 1) for a track to be skipped.
    :return: List of unique track IDs.
    """
    all_keywords = set(seed_words)
    for word in seed_words:
        related_words = get_related_words(word)
        all_keywords.update(related_words)

    print(f"Extended and filtered keywords: {all_keywords}")

    found_tracks = {}
    while len(found_tracks) < length:  # Continue searching until we find at least `length` tracks
        for word in all_keywords:
            # Build the query string
            query = f"{word}"
            if genres:
                query += f" genre:{' '.join(genres)}"
            try:
                results = sp.search(q=query, type='track', limit=10)
                for track in results['tracks']['items']:
                    track_id = track['id']
                    popularity = track['popularity'] / 100  # Convert to 0-1 range
                    # Add randomization to skip some tracks
                    if (track_id not in found_tracks and popularity > 0.5 
                            and random.random() > randomness):
                        found_tracks[track_id] = {
                            'name': track['name'],
                            'artist': track['artists'][0]['name'],
                            'popularity': popularity
                        }
            except Exception as e:
                print(f"Error during search for word {word}: {e}")

            # Stop searching if we've already found the required number of tracks
            if len(found_tracks) >= length:
                break

    # If the number of tracks found is less than length, return only the found tracks
    unique_tracks = list(found_tracks.items())[:length]  # Limit the number of tracks to length
    print(f"Found {len(unique_tracks)} unique tracks.")

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


# Example usage
if __name__ == "__main__":
    user_keywords = ["summer", "beach"]
    user_genre = input("Enter a genre (or leave empty for no restriction): ").strip()

    try:
        # Fetch similar genres or allow no genre restriction
        filtered_genres = get_similar_genres(user_genre if user_genre else None)
        print(f"Filtered genres: {filtered_genres if filtered_genres else 'No genre restriction'}")

        # Fetch unique tracks based on keywords and genres
        tracks = search_songs(sp, user_keywords, genres=filtered_genres, length=20)
        print(f"Fetched {len(tracks)} unique tracks.")

        # Create a playlist with the fetched tracks
        save_tracks(sp, tracks)
    except ValueError as e:
        print(e)
