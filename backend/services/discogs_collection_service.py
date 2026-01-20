# -*- coding: utf-8 -*-
"""
Discogs Collection Service
Adds vinyl records to user's Discogs collection.
"""

import os
import requests
import logging
from typing import Dict, Optional, Any
from backend.services.vinyl_pricing_service import DISCOGS_BASE_URL

logger = logging.getLogger(__name__)

# Discogs API Token (from environment - REQUIRED)
DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")
if not DISCOGS_TOKEN:
    logger.warning("DISCOGS_TOKEN not set - Discogs collection features will be unavailable")


class DiscogsCollectionService:
    """
    Service for adding records to Discogs user collection.
    """
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Discogs token={DISCOGS_TOKEN}",
            "User-Agent": "RecordsAI/1.0",
            "Content-Type": "application/json"
        }
    
    def search_release(
        self,
        artist: str,
        album: str,
        catalog_number: Optional[str] = None,
        label: Optional[str] = None,
        year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search Discogs for a release matching the given metadata.
        Returns the best matching release ID and details.
        """
        if not DISCOGS_TOKEN:
            logger.error("DISCOGS_TOKEN not set - cannot search Discogs")
            return None
        
        try:
            # Build search query
            query_parts = []
            if artist:
                query_parts.append(artist)
            if album:
                query_parts.append(album)
            
            query = " ".join(query_parts)
            
            # Search parameters
            params = {
                "q": query,
                "type": "release",
                "per_page": 10
            }
            
            # Add optional filters
            if catalog_number:
                params["catno"] = catalog_number
            
            url = f"{DISCOGS_BASE_URL}/database/search"
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Discogs search failed: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                logger.warning(f"No Discogs results found for: {artist} - {album}")
                return None
            
            # Find best match
            best_match = self._find_best_match(
                results,
                artist=artist,
                album=album,
                catalog_number=catalog_number,
                label=label,
                year=year
            )
            
            if best_match:
                release_id = best_match.get("id")
                return {
                    "release_id": release_id,
                    "title": best_match.get("title", ""),
                    "artist": best_match.get("artist", ""),
                    "year": best_match.get("year"),
                    "label": best_match.get("label", []),
                    "catno": best_match.get("catno", ""),
                    "thumb": best_match.get("thumb", ""),
                    "url": f"https://www.discogs.com/release/{release_id}",
                    "match_score": best_match.get("match_score", 0.0)
                }
            
            # Return first result if no best match found
            first_result = results[0]
            release_id = first_result.get("id")
            return {
                "release_id": release_id,
                "title": first_result.get("title", ""),
                "artist": first_result.get("artist", ""),
                "year": first_result.get("year"),
                "label": first_result.get("label", []),
                "catno": first_result.get("catno", ""),
                "thumb": first_result.get("thumb", ""),
                "url": f"https://www.discogs.com/release/{release_id}",
                "match_score": 0.5
            }
            
        except Exception as e:
            logger.error(f"Error searching Discogs: {e}")
            return None
    
    def _find_best_match(
        self,
        results: list,
        artist: str,
        album: str,
        catalog_number: Optional[str] = None,
        label: Optional[str] = None,
        year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best matching release from search results.
        Uses fuzzy matching on artist, album, catalog number, label, and year.
        """
        best_match = None
        best_score = 0.0
        
        artist_lower = artist.lower() if artist else ""
        album_lower = album.lower() if album else ""
        catalog_lower = catalog_number.lower() if catalog_number else ""
        label_lower = label.lower() if label else ""
        
        for result in results:
            score = 0.0
            
            # Match artist (40% weight)
            result_artist = result.get("artist", "").lower()
            if artist_lower in result_artist or result_artist in artist_lower:
                score += 0.4
            elif artist_lower and result_artist:
                # Partial match
                if any(word in result_artist for word in artist_lower.split()):
                    score += 0.2
            
            # Match album/title (40% weight)
            result_title = result.get("title", "").lower()
            if album_lower in result_title or result_title in album_lower:
                score += 0.4
            elif album_lower and result_title:
                # Partial match
                if any(word in result_title for word in album_lower.split()):
                    score += 0.2
            
            # Match catalog number (10% weight)
            result_catno = result.get("catno", "").lower()
            if catalog_lower and result_catno and catalog_lower in result_catno:
                score += 0.1
            
            # Match label (5% weight)
            result_labels = result.get("label", [])
            if label_lower:
                for lbl in result_labels:
                    if label_lower in lbl.lower():
                        score += 0.05
                        break
            
            # Match year (5% weight)
            result_year = result.get("year")
            if year and result_year and year == result_year:
                score += 0.05
            
            if score > best_score:
                best_score = score
                best_match = result
                best_match["match_score"] = score
        
        # Only return if match score is reasonable (>0.3)
        if best_score > 0.3:
            return best_match
        
        return None
    
    def add_to_collection(
        self,
        discogs_username: str,
        release_id: int,
        folder_id: int = 0,  # 0 = default "All" folder
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a release to user's Discogs collection.
        
        Args:
            discogs_username: Discogs username
            release_id: Discogs release ID
            folder_id: Collection folder ID (0 = default "All" folder)
            notes: Optional notes about the record
        
        Returns:
            Dict with status and details
        """
        if not DISCOGS_TOKEN:
            return {
                "status": "error",
                "error": "DISCOGS_TOKEN not configured"
            }
        
        try:
            # Add release to collection
            url = f"{DISCOGS_BASE_URL}/users/{discogs_username}/collection/folders/{folder_id}/releases/{release_id}"
            
            data = {}
            if notes:
                data["notes"] = notes
            
            response = requests.post(
                url,
                headers=self.headers,
                json=data if data else None,
                timeout=10
            )
            
            if response.status_code == 201:
                # Successfully added
                return {
                    "status": "ok",
                    "message": f"Release {release_id} added to collection",
                    "release_id": release_id,
                    "folder_id": folder_id,
                    "url": f"https://www.discogs.com/release/{release_id}"
                }
            elif response.status_code == 409:
                # Already in collection
                return {
                    "status": "ok",
                    "message": f"Release {release_id} already in collection",
                    "release_id": release_id,
                    "already_exists": True
                }
            else:
                error_text = response.text
                logger.error(f"Failed to add to Discogs collection: {response.status_code} - {error_text}")
                return {
                    "status": "error",
                    "error": f"Discogs API error: {response.status_code}",
                    "details": error_text
                }
                
        except Exception as e:
            logger.error(f"Error adding to Discogs collection: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_user_folders(self, discogs_username: str) -> Dict[str, Any]:
        """
        Get user's collection folders.
        """
        if not DISCOGS_TOKEN:
            return {
                "status": "error",
                "error": "DISCOGS_TOKEN not configured"
            }
        
        try:
            url = f"{DISCOGS_BASE_URL}/users/{discogs_username}/collection/folders"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                folders = response.json().get("folders", [])
                return {
                    "status": "ok",
                    "folders": folders
                }
            else:
                return {
                    "status": "error",
                    "error": f"Discogs API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error getting Discogs folders: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global instance
discogs_collection_service = DiscogsCollectionService()
