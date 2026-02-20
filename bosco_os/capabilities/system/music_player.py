"""
Bosco Core - Music Player Module
Play music from YouTube using voice commands
"""

import os
import subprocess
import threading
import re
from typing import Optional, Dict, Any
import urllib.parse

# Try to import yt-dlp
try:
    import yt_dlp
    YTDL_AVAILABLE = True
except ImportError:
    YTDL_AVAILABLE = False


class MusicPlayer:
    """
    Music player that streams audio from YouTube
    Supports commands like "play [song] by [artist]"
    """
    
    def __init__(self):
        self.current_process: Optional[subprocess.Popen] = None
        self.current_song: Optional[str] = None
        self.current_artist: Optional[str] = None
        self.is_playing: bool = False
        self.is_paused: bool = False
        
        # Check if mpv is available
        self.mpv_available = self._check_mpv()
        
    def _check_mpv(self) -> bool:
        """Check if mpv is installed"""
        try:
            result = subprocess.run(
                ['which', 'mpv'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_ytdlp(self) -> bool:
        """Check if yt-dlp is installed"""
        return YTDL_AVAILABLE
    
    def parse_song_command(self, command: str) -> Dict[str, str]:
        """
        Parse voice command like "play fear by NF"
        Returns: {'song': 'fear', 'artist': 'NF'}
        """
        command = command.lower().strip()
        
        # Remove common prefixes
        for prefix in ['play ', 'play song ', 'play music ', 'play ', 'bosco play ']:
            if command.startswith(prefix):
                command = command[len(prefix):]
                break
        
        # Try to parse "song by artist" format
        if ' by ' in command:
            parts = command.split(' by ')
            song = parts[0].strip()
            artist = parts[1].strip() if len(parts) > 1 else ''
            return {'song': song, 'artist': artist}
        
        # If no "by", treat entire command as search query
        return {'song': command, 'artist': ''}
    
    def search_youtube(self, query: str) -> Optional[str]:
        """
        Search YouTube and get the best audio stream URL
        """
        if not self._check_ytdlp():
            return None
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for the video
                search_query = f"ytsearch5:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if info and info.get('entries'):
                    # Get the first (most relevant) result
                    video_info = info['entries'][0]
                    video_url = video_info.get('webpage_url')
                    
                    return video_url
        except Exception as e:
            print(f"[Music] Search error: {e}")
        
        return None
    
    def get_audio_url(self, video_url: str) -> Optional[str]:
        """Get direct audio stream URL from video URL"""
        if not self._check_ytdlp():
            return None
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'geturl': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if info and 'url' in info:
                    return info['url']
        except Exception as e:
            print(f"[Music] Audio URL error: {e}")
        
        return None
    
    def play(self, song: str, artist: str = "") -> str:
        """
        Play a song by searching YouTube
        """
        # Stop any currently playing music
        self.stop()
        
        # Build search query
        if artist:
            search_query = f"{song} {artist} audio"
        else:
            search_query = f"{song} audio"
        
        # Search for the song
        video_url = self.search_youtube(search_query)
        
        if not video_url:
            return f"❌ Could not find '{song}' by '{artist}' on YouTube"
        
        # Get audio URL
        audio_url = self.get_audio_url(video_url)
        
        if not audio_url:
            return f"❌ Could not get audio stream for '{song}'"
        
        # Start playing with mpv
        return self._play_stream(audio_url, song, artist)
    
    def _play_stream(self, url: str, song: str, artist: str) -> str:
        """Play audio stream using mpv"""
        
        if not self.mpv_available:
            return "❌ mpv is not installed. Install with: sudo apt install mpv"
        
        try:
            # Kill any existing mpv processes
            subprocess.run(['pkill', '-f', 'mpv'], capture_output=True)
            
            # Start mpv in background mode
            self.current_process = subprocess.Popen(
                ['mpv', '--no-video', '--quiet', '--idle=yes', url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.current_song = song
            self.current_artist = artist
            self.is_playing = True
            self.is_paused = False
            
            if artist:
                return f"🎵 Now playing: {song} by {artist}"
            else:
                return f"🎵 Now playing: {song}"
                
        except Exception as e:
            return f"❌ Error playing music: {str(e)}"
    
    def pause(self) -> str:
        """Pause current playback"""
        if not self.is_playing:
            return "Nothing is playing"
        
        if self.is_paused:
            return "Music is already paused"
        
        try:
            # Send pause command to mpv via IPC
            subprocess.run(
                ['playerctl', '-p', 'mpv', 'pause'],
                capture_output=True
            )
            self.is_paused = True
            return "⏸️ Paused"
        except:
            # Fallback: try to kill and restart
            return "⏸️ Paused (use 'resume' to continue)"
    
    def resume(self) -> str:
        """Resume paused playback"""
        if not self.is_playing:
            return "Nothing is playing"
        
        if not self.is_paused:
            return "Music is not paused"
        
        try:
            subprocess.run(
                ['playerctl', '-p', 'mpv', 'play'],
                capture_output=True
            )
            self.is_paused = False
            return "▶️ Resumed"
        except:
            self.is_paused = False
            return "▶️ Resumed"
    
    def stop(self) -> str:
        """Stop playback"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=2)
            except:
                self.current_process.kill()
            self.current_process = None
        
        # Also kill any mpv processes
        subprocess.run(['pkill', '-f', 'mpv'], capture_output=True)
        
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.current_artist = None
        
        return "⏹️ Stopped playing"
    
    def next(self) -> str:
        """Skip to next song (not implemented for YouTube streams)"""
        return "⏭️ Next song not available for YouTube streams. Say 'stop' to stop and play something else."
    
    def previous(self) -> str:
        """Go to previous song (not implemented for YouTube streams)"""
        return "⏮️ Previous song not available for YouTube streams."
    
    def status(self) -> str:
        """Get current playback status"""
        if not self.is_playing:
            return "No music playing"
        
        status = "▶️ Playing" if not self.is_paused else "⏸️ Paused"
        
        if self.current_artist:
            return f"{status}: {self.current_song} by {self.current_artist}"
        else:
            return f"{status}: {self.current_song}"


# Global music player instance
_music_player = None


def get_music_player() -> MusicPlayer:
    """Get the global music player instance"""
    global _music_player
    if _music_player is None:
        _music_player = MusicPlayer()
    return _music_player


def play_music(song: str, artist: str = "") -> str:
    """Play a song"""
    return get_music_player().play(song, artist)


def stop_music() -> str:
    """Stop music"""
    return get_music_player().stop()


def pause_music() -> str:
    """Pause music"""
    return get_music_player().pause()


def resume_music() -> str:
    """Resume music"""
    return get_music_player().resume()


def music_status() -> str:
    """Get music status"""
    return get_music_player().status()


if __name__ == "__main__":
    # Test the music player
    print("=== Testing Music Player ===\n")
    
    player = get_music_player()
    
    print(f"mpv available: {player.mpv_available}")
    print(f"yt-dlp available: {player._check_ytdlp()}")
    
    # Test parsing
    test_commands = [
        "play fear by NF",
        "play shape of you",
        "play despacito",
        "play Bohemian Rhapsody by Queen"
    ]
    
    print("\nParsing tests:")
    for cmd in test_commands:
        result = player.parse_song_command(cmd)
        print(f"  '{cmd}' -> {result}")
    
    # Test actual playback (uncomment to test)
    # print("\nPlaying test...")
    # result = player.play("Hello by Adele")
    # print(result)

