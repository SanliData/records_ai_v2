# -*- coding: utf-8 -*-
"""
Lyrics Service
Fetches song lyrics links from various sources (Genius, Lyrics.com, Lyrics.ovh).
"""

import requests
import urllib.parse
from typing import Dict, Optional, List
import time


class LyricsService:
    """
    Service for fetching song lyrics links from various sources.
    """
    
    def __init__(self):
        self.headers = {
            "User-Agent": "RecordsAI/1.0"
        }
    
    def get_lyrics_links(
        self,
        artist: str,
        song_title: str,
        album: Optional[str] = None
    ) -> Dict:
        """
        Get lyrics links from various sources.
        
        Returns:
        {
            "lyrics_links": [
                {
                    "source": "genius",
                    "url": "https://genius.com/...",
                    "title": "Song Title"
                },
                ...
            ],
            "play_links": [...],  # Spotify, YouTube, etc.
            "sources": ["genius", "lyrics.com", "lyricsify"]
        }
        """
        if not artist or not song_title:
            return self._empty_lyrics()
        
        links = []
        
        # 1. Genius (most comprehensive)
        genius_link = self._get_genius_link(artist, song_title)
        if genius_link:
            links.append({
                "source": "genius",
                "name": "Genius",
                "url": genius_link,
                "title": f"{artist} - {song_title}"
            })
        
        # 2. Lyrics.com
        lyrics_com_link = self._get_lyrics_com_link(artist, song_title)
        if lyrics_com_link:
            links.append({
                "source": "lyrics.com",
                "name": "Lyrics.com",
                "url": lyrics_com_link,
                "title": f"{artist} - {song_title}"
            })
        
        # 3. Lyricsify
        lyricsify_link = self._get_lyricsify_link(artist, song_title)
        if lyricsify_link:
            links.append({
                "source": "lyricsify",
                "name": "Lyricsify",
                "url": lyricsify_link,
                "title": f"{artist} - {song_title}"
            })
        
        # 4. Lyrics.ovh (free API, direct lyrics)
        lyrics_ovh_data = self._get_lyrics_ovh(artist, song_title)
        
        # 5. Play links (Spotify, YouTube)
        play_links = self._get_play_links(artist, song_title)
        
        return {
            "lyrics_links": links,
            "play_links": play_links,
            "lyrics_ovh": lyrics_ovh_data,
            "sources": [link["source"] for link in links],
            "artist": artist,
            "song_title": song_title,
            "album": album
        }
    
    def _get_genius_link(self, artist: str, song_title: str) -> Optional[str]:
        """Get Genius lyrics URL."""
        try:
            # Genius URL format: https://genius.com/artist-song-title-lyrics
            # Sanitize for URL
            artist_slug = artist.lower().replace(" ", "-").replace("'", "")
            song_slug = song_title.lower().replace(" ", "-").replace("'", "")
            url = f"https://genius.com/{artist_slug}-{song_slug}-lyrics"
            return url
        except Exception as e:
            print(f"[LyricsService] Genius link error: {e}")
            return None
    
    def _get_lyrics_com_link(self, artist: str, song_title: str) -> Optional[str]:
        """Get Lyrics.com URL."""
        try:
            # Lyrics.com URL format: https://www.lyrics.com/lyric/... or search
            artist_encoded = urllib.parse.quote(artist)
            song_encoded = urllib.parse.quote(song_title)
            # Search URL as direct link may not work
            url = f"https://www.lyrics.com/lyrics/{artist_encoded}%20{song_encoded}"
            return url
        except Exception as e:
            print(f"[LyricsService] Lyrics.com link error: {e}")
            return None
    
    def _get_lyricsify_link(self, artist: str, song_title: str) -> Optional[str]:
        """Get Lyricsify URL."""
        try:
            # Lyricsify URL format: https://www.lyricsify.com/...
            artist_slug = artist.lower().replace(" ", "-")
            song_slug = song_title.lower().replace(" ", "-")
            url = f"https://www.lyricsify.com/search?q={artist_slug}+{song_slug}"
            return url
        except Exception as e:
            print(f"[LyricsService] Lyricsify link error: {e}")
            return None
    
    def _get_lyrics_ovh(self, artist: str, song_title: str) -> Optional[Dict]:
        """Get lyrics from Lyrics.ovh (free API)."""
        try:
            # Lyrics.ovh free API
            artist_encoded = urllib.parse.quote(artist)
            song_encoded = urllib.parse.quote(song_title)
            url = f"https://api.lyrics.ovh/v1/{artist_encoded}/{song_encoded}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                lyrics_text = data.get("lyrics", "")
                if lyrics_text:
                    return {
                        "source": "lyrics.ovh",
                        "lyrics_text": lyrics_text,
                        "has_lyrics": True
                    }
        except Exception as e:
            print(f"[LyricsService] Lyrics.ovh error: {e}")
        
        return None
    
    def _get_play_links(self, artist: str, song_title: str) -> List[Dict]:
        """Get play links (Spotify, YouTube)."""
        links = []
        
        # Spotify search URL
        query = f"{artist} {song_title}".replace(" ", "+")
        spotify_url = f"https://open.spotify.com/search/{urllib.parse.quote(query)}"
        links.append({
            "source": "spotify",
            "name": "Spotify",
            "url": spotify_url
        })
        
        # YouTube search URL
        youtube_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        links.append({
            "source": "youtube",
            "name": "YouTube",
            "url": youtube_url
        })
        
        return links
    
    def _empty_lyrics(self) -> Dict:
        """Return empty lyrics structure."""
        return {
            "lyrics_links": [],
            "play_links": [],
            "lyrics_ovh": None,
            "sources": [],
            "artist": None,
            "song_title": None,
            "album": None
        }


# Global instance
lyrics_service = LyricsService()
