# playlistify
Creation of spotify playlist made of user-entered parameters

## Features

- Create Spotify playlists based on:
  - User-defined keywords
  - Genres
  - Pre-defined presets
- Leverage ConceptNet for generating related keywords to broaden search results.
- Save generated playlists directly to a Spotify account.
- Simple web interface built with Flask for user interaction.

## Requirements

- Python 3.8 or later
- Spotify Developer Account for API credentials
- A Spotify Premium account (required for playlist modifications)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kingaleibner/playlistify
2. Install the required packages:
    pip install -r requirements.txt
3. Set up Spotify API credentials:
    - Create a Spotify Developer account
    - Create an application and obtain your CLIENT_ID and CLIENT_SECRET
    - Update credentials in the code
4. Run the application:
    python main.py
5. Open your browser and go to http://localhost:5000.

## Usage

1. Open the application in your browser.
2. Choose to:
    - **Create a playlist from a preset:** Select from a list of pre-configured presets.
    - **Customize your playlist:** Enter seed words, genres, and define playlist length.


## System Architecture

### 1. Architecture Overview

The system is built using the following components:
- **Frontend**: A simple Flask-based web interface to interact with users.
- **Backend**: Python code that handles the logic for generating playlists, calling APIs, and saving results.

### 2. Technology Stack

| Component          | Technology               |
|--------------------|--------------------------|
| Web Framework      | Flask                    |
| API Integration    | Spotify API, ConceptNet API |
| Programming Language | Python                  |
| Data Storage       | JSON files for presets   |

---

## Key Components

### 1. Spotify API

#### Purpose
- Authenticate users via OAuth.
- Fetch tracks based on search queries.
- Create and modify playlists.

#### Integration
- Uses the `spotipy` library for handling Spotify API calls.
- Requires a `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI`.

### 2. ConceptNet API

#### Purpose
- Generate related words to enhance search queries.

#### Integration
- Makes HTTP GET requests using the `requests` library.
- Filters results to include only related words of a minimum weight and removes antonyms.

---

## Functionalities

### 1. Create Playlist from Presets
- Users can select a preset from predefined configurations.
- Presets include seed words, genres, and playlist names.

### 2. Custom Playlist Generation
- Users can enter:
  - Keywords: Words used to find related tracks.
  - Genres: Spotify-supported genres to refine search results.
  - Length: Number of tracks in the playlist.
- The system combines user input with related words from ConceptNet.

---

## Workflow

1. **User Input**:
   - Enter seed words, genres, or select a preset.
2. **Related Word Generation**:
   - ConceptNet API fetches related terms.
3. **Track Search**:
   - Spotify API searches for tracks matching keywords and genres.
4. **Playlist Creation**:
   - Save selected tracks to a new playlist in the user's Spotify account.

---

## APIs Used

### Spotify API
- **Endpoints**:
  - `/search`: Fetch tracks based on keywords and genres.
  - `/me`: Get user profile details.
  - `/playlists`: Create and modify playlists.
- **Authentication**:
  - OAuth with `spotipy`.

### ConceptNet API
- **Endpoint**:
  - `/related`: Fetch related words for a given keyword.
- **Authentication**:
  - None required.

---

## Future Enhancements

- Add a recommendation engine based on user listening history.
- Improve error handling for API rate limits.
- Enable multi-language support for ConceptNet queries.