# -*- coding: utf-8 -*-
"""
Sheet Music Service
Generates sheet music links from various sources (IMSLP, MuseScore, Free-scores).
"""

import urllib.parse
from typing import Dict, Optional, List


class SheetMusicService:
    """
    Service for generating sheet music links from various sources.
    """
    
    def __init__(self):
        pass
    
    def get_sheet_music_links(
        self,
        artist: str,
        song_title: str,
        album: Optional[str] = None,
        composer: Optional[str] = None
    ) -> Dict:
        """
        Get sheet music links from various sources.
        
        Returns:
        {
            "sheet_music_links": [
                {
                    "source": "imslp",
                    "name": "IMSLP",
                    "url": "https://imslp.org/...",
                    "title": "..."
                },
                ...
            ],
            "sources": ["imslp", "musescore", "free-scores"]
        }
        """
        if not artist or not song_title:
            return self._empty_sheet_music()
        
        links = []
        
        # 1. IMSLP (classical music)
        imslp_link = self._get_imslp_link(artist, song_title, composer)
        if imslp_link:
            links.append({
                "source": "imslp",
                "name": "IMSLP",
                "url": imslp_link,
                "title": f"{artist} - {song_title}",
                "type": "classical"
            })
        
        # 2. MuseScore.com
        musescore_link = self._get_musescore_link(artist, song_title)
        if musescore_link:
            links.append({
                "source": "musescore",
                "name": "MuseScore",
                "url": musescore_link,
                "title": f"{artist} - {song_title}",
                "type": "community"
            })
        
        # 3. Free-scores.com
        free_scores_link = self._get_free_scores_link(artist, song_title)
        if free_scores_link:
            links.append({
                "source": "free-scores",
                "name": "Free-scores.com",
                "url": free_scores_link,
                "title": f"{artist} - {song_title}",
                "type": "mixed"
            })
        
        # 4. Musopen.org
        musopen_link = self._get_musopen_link(artist, song_title, composer)
        if musopen_link:
            links.append({
                "source": "musopen",
                "name": "Musopen",
                "url": musopen_link,
                "title": f"{artist} - {song_title}",
                "type": "public_domain"
            })
        
        # 5. 8Notes.com (lessons and sheet music)
        eightnotes_link = self._get_8notes_link(artist, song_title)
        if eightnotes_link:
            links.append({
                "source": "8notes",
                "name": "8Notes.com",
                "url": eightnotes_link,
                "title": f"{artist} - {song_title}",
                "type": "lessons"
            })
        
        return {
            "sheet_music_links": links,
            "sources": [link["source"] for link in links],
            "artist": artist,
            "song_title": song_title,
            "album": album,
            "composer": composer
        }
    
    def _get_imslp_link(self, artist: str, song_title: str, composer: Optional[str] = None) -> Optional[str]:
        """Get IMSLP link (International Music Score Library Project)."""
        try:
            # IMSLP uses composer name, not artist
            search_term = composer or artist
            search_encoded = urllib.parse.quote(search_term)
            url = f"https://imslp.org/wiki/Special:Search?search={search_encoded}+{urllib.parse.quote(song_title)}"
            return url
        except Exception as e:
            print(f"[SheetMusicService] IMSLP link error: {e}")
            return None
    
    def _get_musescore_link(self, artist: str, song_title: str) -> Optional[str]:
        """Get MuseScore.com link."""
        try:
            query = f"{artist} {song_title}"
            query_encoded = urllib.parse.quote(query)
            url = f"https://musescore.com/sheetmusic?text={query_encoded}"
            return url
        except Exception as e:
            print(f"[SheetMusicService] MuseScore link error: {e}")
            return None
    
    def _get_free_scores_link(self, artist: str, song_title: str) -> Optional[str]:
        """Get Free-scores.com link."""
        try:
            query = f"{artist} {song_title}"
            query_encoded = urllib.parse.quote(query)
            url = f"https://www.free-scores.com/search.php?pays=&st={query_encoded}"
            return url
        except Exception as e:
            print(f"[SheetMusicService] Free-scores link error: {e}")
            return None
    
    def _get_musopen_link(self, artist: str, song_title: str, composer: Optional[str] = None) -> Optional[str]:
        """Get Musopen.org link."""
        try:
            search_term = composer or artist
            query = f"{search_term} {song_title}"
            query_encoded = urllib.parse.quote(query)
            url = f"https://musopen.org/music/?q={query_encoded}"
            return url
        except Exception as e:
            print(f"[SheetMusicService] Musopen link error: {e}")
            return None
    
    def _get_8notes_link(self, artist: str, song_title: str) -> Optional[str]:
        """Get 8Notes.com link."""
        try:
            query = f"{artist} {song_title}"
            query_encoded = urllib.parse.quote(query)
            url = f"https://www.8notes.com/search.asp?q={query_encoded}"
            return url
        except Exception as e:
            print(f"[SheetMusicService] 8Notes link error: {e}")
            return None
    
    def _empty_sheet_music(self) -> Dict:
        """Return empty sheet music structure."""
        return {
            "sheet_music_links": [],
            "sources": [],
            "artist": None,
            "song_title": None,
            "album": None,
            "composer": None
        }


# Global instance
sheet_music_service = SheetMusicService()
