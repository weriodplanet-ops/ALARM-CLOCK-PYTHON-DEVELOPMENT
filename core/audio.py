"""
Audio management for alarm tones.
"""

import os
from typing import Optional
from tones.default_tones import TONES

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class AudioManager:
    """
    Manages audio playback for alarm tones.
    """

    def __init__(self):
        """
        Initialize AudioManager.
        """
        self.current_sound = None
        self.is_playing = False

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Warning: Could not initialize pygame mixer: {e}")
                print("Audio playback may not work correctly.")

    def play_tone(self, tone_name: str, loop: bool = True) -> bool:
        """
        Play an alarm tone.

        Args:
            tone_name: Name of the tone to play
            loop: Whether to loop the tone

        Returns:
            True if tone was played, False otherwise
        """
        if not PYGAME_AVAILABLE:
            print(f"⏹️  Tone '{tone_name}' (pygame not available - using fallback)")
            self._print_tone_warning()
            return False

        try:
            # Try to load custom audio file
            if tone_name in TONES:
                audio_file = TONES[tone_name]
                if os.path.exists(audio_file):
                    sound = pygame.mixer.Sound(audio_file)
                    loops = -1 if loop else 0
                    sound.play(loops)
                    self.current_sound = sound
                    self.is_playing = True
                    print(f"🔊 Playing tone: {tone_name}")
                    return True
            else:
                print(f"⚠️  Tone '{tone_name}' not found. Available tones: {list(TONES.keys())}")
                return False

        except Exception as e:
            print(f"Error playing tone: {e}")
            return False

    def stop(self) -> None:
        """
        Stop current audio playback.
        """
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.stop()
                self.is_playing = False
                print("🔇 Audio stopped")
            except Exception as e:
                print(f"Error stopping audio: {e}")

    def _print_tone_warning(self) -> None:
        """
        Print warning about missing pygame.
        """
        print("\n" + "="*50)
        print("⚠️  pygame is not installed")
        print("Install it with: pip install pygame")
        print("="*50 + "\n")

    @staticmethod
    def get_available_tones() -> list:
        """
        Get list of available tone names.

        Returns:
            List of available tone names
        """
        return list(TONES.keys())
