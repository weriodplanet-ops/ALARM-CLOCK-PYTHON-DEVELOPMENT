#!/usr/bin/env python3
"""
Audio tone generator for alarm clock application.
Generates WAV files for all alarm tones.
"""

import os
import wave
import struct
import math
from typing import List, Tuple


class ToneGenerator:
    """
    Generates WAV audio files for alarm tones.
    """

    def __init__(self, sample_rate: int = 44100, duration: float = 3.0):
        """
        Initialize ToneGenerator.

        Args:
            sample_rate: Sample rate in Hz (default 44100)
            duration: Duration of tone in seconds (default 3.0)
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_samples = int(sample_rate * duration)

    def _generate_sine_wave(self, frequency: float, volume: float = 0.3) -> List[int]:
        """
        Generate a sine wave at specified frequency.

        Args:
            frequency: Frequency in Hz
            volume: Volume level (0.0 to 1.0)

        Returns:
            List of audio samples
        """
        samples = []
        for i in range(self.num_samples):
            sample = volume * math.sin(2.0 * math.pi * frequency * i / self.sample_rate)
            samples.append(int(sample * 32767))  # Convert to 16-bit
        return samples

    def _generate_square_wave(self, frequency: float, volume: float = 0.3) -> List[int]:
        """
        Generate a square wave at specified frequency.

        Args:
            frequency: Frequency in Hz
            volume: Volume level (0.0 to 1.0)

        Returns:
            List of audio samples
        """
        samples = []
        period = self.sample_rate / frequency
        for i in range(self.num_samples):
            if (i % period) < (period / 2):
                sample = volume
            else:
                sample = -volume
            samples.append(int(sample * 32767))
        return samples

    def _apply_envelope(self, samples: List[int], attack: float = 0.1, release: float = 0.2) -> List[int]:
        """
        Apply attack and release envelope to samples.

        Args:
            samples: Original samples
            attack: Attack time in seconds
            release: Release time in seconds

        Returns:
            Samples with envelope applied
        """
        attack_samples = int(self.sample_rate * attack)
        release_samples = int(self.sample_rate * release)

        for i in range(len(samples)):
            # Attack
            if i < attack_samples:
                envelope = i / attack_samples
                samples[i] = int(samples[i] * envelope)
            # Release
            elif i > len(samples) - release_samples:
                envelope = (len(samples) - i) / release_samples
                samples[i] = int(samples[i] * envelope)

        return samples

    def _save_wav(self, filename: str, samples: List[int], num_channels: int = 1) -> None:
        """
        Save samples to WAV file.

        Args:
            filename: Output filename
            samples: Audio samples
            num_channels: Number of audio channels
        """
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)

            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))

    def generate_digital_beep(self, filename: str) -> None:
        """
        Generate sharp digital beep tone.
        """
        print(f"Generating digital beep: {filename}")
        # Create a pattern of beeps: 1000Hz for 0.2s, rest 0.1s, repeat
        samples = []
        beep_duration = 0.2
        rest_duration = 0.1
        beep_samples = int(self.sample_rate * beep_duration)
        rest_samples = int(self.sample_rate * rest_duration)
        pattern_repeats = int(self.duration / (beep_duration + rest_duration))

        for _ in range(pattern_repeats):
            # Beep
            beep = self._generate_sine_wave(1000, 0.4)[:beep_samples]
            beep = self._apply_envelope(beep, attack=0.01, release=0.05)
            samples.extend(beep)
            # Rest
            samples.extend([0] * rest_samples)

        # Pad to exact duration
        while len(samples) < self.num_samples:
            samples.append(0)
        samples = samples[:self.num_samples]

        self._save_wav(filename, samples)

    def generate_classic_alarm(self, filename: str) -> None:
        """
        Generate classic alarm clock sound (alternating tones).
        """
        print(f"Generating classic alarm: {filename}")
        samples = []
        beep_duration = 0.15
        beep_samples = int(self.sample_rate * beep_duration)
        pattern_repeats = int(self.duration / beep_duration)

        for i in range(pattern_repeats):
            # Alternate between two frequencies
            frequency = 1200 if i % 2 == 0 else 900
            beep = self._generate_sine_wave(frequency, 0.35)[:beep_samples]
            beep = self._apply_envelope(beep, attack=0.01, release=0.02)
            samples.extend(beep)

        # Pad to exact duration
        while len(samples) < self.num_samples:
            samples.append(0)
        samples = samples[:self.num_samples]

        self._save_wav(filename, samples)

    def generate_gentle_tone(self, filename: str) -> None:
        """
        Generate soft and gradual wake-up tone.
        """
        print(f"Generating gentle tone: {filename}")
        # Slow sine wave sweep: 300Hz to 600Hz
        samples = []
        for i in range(self.num_samples):
            progress = i / self.num_samples
            frequency = 300 + (300 * progress)  # Sweep from 300 to 600 Hz
            sample = 0.25 * math.sin(2.0 * math.pi * frequency * i / self.sample_rate)
            samples.append(int(sample * 32767))

        # Apply gentle envelope
        samples = self._apply_envelope(samples, attack=0.5, release=0.3)
        self._save_wav(filename, samples)

    def generate_buzzer(self, filename: str) -> None:
        """
        Generate loud buzzer sound.
        """
        print(f"Generating buzzer: {filename}")
        # Use square wave for harsh buzzer sound
        samples = []
        buzz_duration = 0.1
        buzz_samples = int(self.sample_rate * buzz_duration)
        pattern_repeats = int(self.duration / buzz_duration)

        for _ in range(pattern_repeats):
            buzz = self._generate_square_wave(500, 0.5)[:buzz_samples]
            buzz = self._apply_envelope(buzz, attack=0.01, release=0.02)
            samples.extend(buzz)

        # Pad to exact duration
        while len(samples) < self.num_samples:
            samples.append(0)
        samples = samples[:self.num_samples]

        self._save_wav(filename, samples)

    def generate_chime(self, filename: str) -> None:
        """
        Generate pleasant chime notification.
        """
        print(f"Generating chime: {filename}")
        samples = []
        notes = [523, 659, 784]  # C5, E5, G5 - pleasant chord
        note_duration = 0.3
        note_samples = int(self.sample_rate * note_duration)
        repeats = int(self.duration / note_duration)

        for rep in range(repeats):
            # Mix all notes
            note_samp = [0] * note_samples
            for note_freq in notes:
                note_wave = self._generate_sine_wave(note_freq, 0.2)[:note_samples]
                for i in range(note_samples):
                    note_samp[i] += note_wave[i]

            # Average to prevent clipping
            note_samp = [int(s / len(notes)) for s in note_samp]
            note_samp = self._apply_envelope(note_samp, attack=0.05, release=0.2)
            samples.extend(note_samp)

        # Pad to exact duration
        while len(samples) < self.num_samples:
            samples.append(0)
        samples = samples[:self.num_samples]

        self._save_wav(filename, samples)

    def generate_all_tones(self, output_dir: str = "audio_files") -> None:
        """
        Generate all alarm tones.

        Args:
            output_dir: Output directory for WAV files
        """
        os.makedirs(output_dir, exist_ok=True)

        self.generate_digital_beep(os.path.join(output_dir, "digital.wav"))
        self.generate_classic_alarm(os.path.join(output_dir, "classic.wav"))
        self.generate_gentle_tone(os.path.join(output_dir, "gentle.wav"))
        self.generate_buzzer(os.path.join(output_dir, "buzzer.wav"))
        self.generate_chime(os.path.join(output_dir, "chime.wav"))

        print(f"\n✅ All tone files generated successfully in '{output_dir}' directory!")


def main():
    """
    Generate all alarm tones.
    """
    print("🎵 Alarm Tone Generator")
    print("=======================")
    print()

    generator = ToneGenerator(sample_rate=44100, duration=3.0)
    generator.generate_all_tones()

    print()
    print("To use these tones:")
    print("1. Run: python main.py")
    print("2. Create a new alarm and select your preferred tone")
    print("3. The alarm will use the generated audio file!")
    print()


if __name__ == "__main__":
    main()
