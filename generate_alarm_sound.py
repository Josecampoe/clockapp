"""Utility script to generate the alarm_sound.wav file.

Run this once after installing Python:
    python generate_alarm_sound.py
"""

import struct
import wave
import math
import os


def generate_alarm_wav(output_path: str) -> None:
    """Generate a simple two-tone beep WAV file.

    Args:
        output_path: Destination path for the WAV file.
    """
    sample_rate = 44100
    amplitude = 16000
    duration_per_beep = 0.25  # seconds
    silence_duration = 0.05   # seconds between beeps
    num_beeps = 4
    frequencies = [880, 1100]  # alternating tones

    all_samples: list = []

    for beep_idx in range(num_beeps):
        freq = frequencies[beep_idx % len(frequencies)]
        num_samples = int(sample_rate * duration_per_beep)
        for i in range(num_samples):
            t = i / sample_rate
            env = min(t * 20, 1.0, (duration_per_beep - t) * 20)
            val = int(amplitude * env * math.sin(2 * math.pi * freq * t))
            all_samples.append(val)
        # Silence between beeps
        silence_samples = int(sample_rate * silence_duration)
        all_samples.extend([0] * silence_samples)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        data = struct.pack("<" + "h" * len(all_samples), *all_samples)
        wf.writeframes(data)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    _out = os.path.join(os.path.dirname(__file__), "assets", "alarm_sound.wav")
    generate_alarm_wav(_out)
