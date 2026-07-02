"""
Alarm Manager for managing multiple alarms.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Callable
from threading import Thread, Lock
import time

from core.alarm import Alarm, AlarmStatus
from core.audio import AudioManager


class AlarmManager:
    """
    Manages collection of alarms and coordinates their triggering.
    """

    def __init__(self, data_file: str = "data/alarms.json"):
        """
        Initialize AlarmManager.

        Args:
            data_file: Path to JSON file for persistent storage
        """
        self.data_file = data_file
        self.alarms: List[Alarm] = []
        self.audio_manager = AudioManager()
        self.running = False
        self.lock = Lock()
        self.alarm_callbacks: List[Callable[[Alarm], None]] = []
        self.stop_callbacks: List[Callable[[Alarm], None]] = []
        self._ensure_data_directory()
        self.load_alarms()

    def _ensure_data_directory(self) -> None:
        """
        Ensure data directory exists.
        """
        os.makedirs(os.path.dirname(self.data_file) or ".", exist_ok=True)

    def add_alarm(self, alarm: Alarm) -> None:
        """
        Add a new alarm.

        Args:
            alarm: Alarm instance to add
        """
        with self.lock:
            self.alarms.append(alarm)
        self.save_alarms()

    def remove_alarm(self, alarm_id: str) -> bool:
        """
        Remove an alarm by ID.

        Args:
            alarm_id: ID of alarm to remove

        Returns:
            True if alarm was removed, False if not found
        """
        with self.lock:
            initial_length = len(self.alarms)
            self.alarms = [a for a in self.alarms if a.id != alarm_id]
            removed = len(self.alarms) < initial_length

        if removed:
            self.save_alarms()
        return removed

    def get_alarm(self, alarm_id: str) -> Optional[Alarm]:
        """
        Get alarm by ID.

        Args:
            alarm_id: ID of alarm to retrieve

        Returns:
            Alarm instance or None if not found
        """
        with self.lock:
            for alarm in self.alarms:
                if alarm.id == alarm_id:
                    return alarm
        return None

    def get_all_alarms(self) -> List[Alarm]:
        """
        Get all alarms.

        Returns:
            List of all alarms
        """
        with self.lock:
            return self.alarms.copy()

    def update_alarm(self, alarm: Alarm) -> None:
        """
        Update an existing alarm.

        Args:
            alarm: Updated alarm instance
        """
        with self.lock:
            for i, a in enumerate(self.alarms):
                if a.id == alarm.id:
                    self.alarms[i] = alarm
                    break
        self.save_alarms()

    def register_alarm_callback(self, callback: Callable[[Alarm], None]) -> None:
        """
        Register callback for when alarm triggers.

        Args:
            callback: Function called with Alarm when it triggers
        """
        self.alarm_callbacks.append(callback)

    def register_stop_callback(self, callback: Callable[[Alarm], None]) -> None:
        """
        Register callback for when alarm is stopped.

        Args:
            callback: Function called with Alarm when it's stopped
        """
        self.stop_callbacks.append(callback)

    def start(self) -> None:
        """
        Start monitoring alarms in background thread.
        """
        if not self.running:
            self.running = True
            thread = Thread(target=self._monitor_loop, daemon=True)
            thread.start()

    def stop(self) -> None:
        """
        Stop monitoring alarms.
        """
        self.running = False
        self.audio_manager.stop()

    def _monitor_loop(self) -> None:
        """
        Background thread loop that monitors alarms.
        """
        while self.running:
            try:
                with self.lock:
                    for alarm in self.alarms:
                        if alarm.is_ringing():
                            self._trigger_alarm(alarm)
                time.sleep(1)
            except Exception as e:
                print(f"Error in alarm monitor: {e}")

    def _trigger_alarm(self, alarm: Alarm) -> None:
        """
        Trigger an alarm (play sound and call callbacks).

        Args:
            alarm: Alarm to trigger
        """
        print(f"🔔 Alarm triggered: {alarm.name}")
        self.audio_manager.play_tone(alarm.tone)

        for callback in self.alarm_callbacks:
            try:
                callback(alarm)
            except Exception as e:
                print(f"Error in alarm callback: {e}")

    def snooze_alarm(self, alarm_id: str, minutes: Optional[int] = None) -> bool:
        """
        Snooze an alarm.

        Args:
            alarm_id: ID of alarm to snooze
            minutes: Snooze duration (uses default if None)

        Returns:
            True if alarm was snoozed, False if not found
        """
        alarm = self.get_alarm(alarm_id)
        if alarm:
            alarm.snooze(minutes)
            self.audio_manager.stop()
            self.update_alarm(alarm)
            print(f"😴 Snoozed: {alarm.name}")
            return True
        return False

    def stop_alarm(self, alarm_id: str) -> bool:
        """
        Stop an alarm.

        Args:
            alarm_id: ID of alarm to stop

        Returns:
            True if alarm was stopped, False if not found
        """
        alarm = self.get_alarm(alarm_id)
        if alarm:
            alarm.stop()
            self.audio_manager.stop()
            self.update_alarm(alarm)
            print(f"⏸️  Stopped: {alarm.name}")

            for callback in self.stop_callbacks:
                try:
                    callback(alarm)
                except Exception as e:
                    print(f"Error in stop callback: {e}")
            return True
        return False

    def save_alarms(self) -> None:
        """
        Save alarms to JSON file.
        """
        try:
            with self.lock:
                data = [alarm.to_dict() for alarm in self.alarms]
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving alarms: {e}")

    def load_alarms(self) -> None:
        """
        Load alarms from JSON file.
        """
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                with self.lock:
                    self.alarms = [Alarm.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error loading alarms: {e}")
            self.alarms = []

    def __repr__(self) -> str:
        return f"AlarmManager(alarms={len(self.alarms)})"
