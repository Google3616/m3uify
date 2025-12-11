import sys
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CONFIG_FILE = "config.json"


def save_config(client_id, client_secret):
    config = {
        "SPOTIFY_CLIENT_ID": client_id,
        "SPOTIFY_CLIENT_SECRET": client_secret
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    print("✅ Credentials saved to config.json")
    print("Run again with: python playlistify.py <playlist_url>")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("❌ ERROR: No credentials found!")
        print("Set credentials using:")
        print("python playlistify.py -config CLIENT_ID CLIENT_SECRET")
        sys.exit(1)

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return config["SPOTIFY_CLIENT_ID"], config["SPOTIFY_CLIENT_SECRET"]


def create_m3u_from_playlist(url):
    client_id, client_secret = load_config()

    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
    )

    playlist = sp.playlist(url)
    playlist_name = playlist["name"].replace("/", "_").replace("\\", "_")
    m3u_filename = f"{playlist_name}.m3u"

    print(f"🎵 Creating playlist: {m3u_filename}")

    tracks = []
    results = playlist["tracks"]

    while results:
        for item in results["items"]:
            if item["track"]:
                tracks.append(item["track"])
        results = sp.next(results) if results["next"] else None

    with open(m3u_filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for track in tracks:
            title = track["name"]
            artists = ", ".join(a["name"] for a in track["artists"])
            f.write(f"{artists} - {title}\n")

    print(f"✅ Done! Saved: {m3u_filename}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "-config":
        if len(sys.argv) != 4:
            print("Usage: python playlistify.py -config CLIENT_ID CLIENT_SECRET")
            sys.exit(1)

        save_config(sys.argv[2], sys.argv[3])
        sys.exit(0)

    # Regular execution
    if len(sys.argv) != 2:
        
        print("Usage:")
        print("  python playlistify.py -config CLIENT_ID CLIENT_SECRET")
        print("  python playlistify.py <spotify_playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]
    create_m3u_from_playlist(playlist_url)
