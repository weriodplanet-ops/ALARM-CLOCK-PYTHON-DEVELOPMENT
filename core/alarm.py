"""
Alarm class for managing individual alarms.
"""

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
import uuid


class AlarmStatus(Enum):
    """Alarm status enumeration."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    RINGING = "ringing"
    SNOOZED = "snoozed"
    STOPPED = "stopped"


class Alarm:
    """
    Represents a single alarm with customizable properties.
    """

    def __init__(
        self,
        name: str,
        time: datetime,
        tone: str = "digital",
        repeat: str = "once",
        enabled: bool = True,
        snooze_duration: int = 5,
        alarm_id: Optional[str] = None
    ):
        """
        Initialize an Alarm.

        Args:
            name: Display name for the alarm
            time: Time when alarm should trigger
            tone: Alarm tone name
            repeat: Repeat pattern ("once", "daily", "weekdays")
            enabled: Whether alarm is enabled
            snooze_duration: Default snooze time in minutes
            alarm_id: Unique identifier (auto-generated if not provided)
        """
        self.id = alarm_id or str(uuid.uuid4())
        self.name = name
        self.time = time
        self.tone = tone
        self.repeat = repeat
        self.enabled = enabled
        self.snooze_duration = snooze_duration
        self.status = AlarmStatus.INACTIVE
        self.next_trigger = self._calculate_next_trigger()
        self.snooze_until: Optional[datetime] = None

    def _calculate_next_trigger(self) -> datetime:
        """
        Calculate the next trigger time for this alarm.

        Returns:
            Next datetime when alarm should trigger
        """
        now = datetime.now()
        next_time = self.time.replace(
            year=now.year,
            month=now.month,
            day=now.day
        )

        if next_time <= now:
            if self.repeat == "once":
                next_time += timedelta(days=1)
            elif self.repeat == "daily":
                next_time += timedelta(days=1)
            elif self.repeat == "weekdays":
                next_time += timedelta(days=1)
                while next_time.weekday() >= 5:  # Skip weekends
                    next_time += timedelta(days=1)

        return next_time

    def snooze(self, minutes: Optional[int] = None) -> None:
        """
        Snooze the alarm for specified minutes.

        Args:
            minutes: Snooze duration in minutes (uses default if None)
        """
        duration = minutes or self.snooze_duration
        self.snooze_until = datetime.now() + timedelta(minutes=duration)
        self.status = AlarmStatus.SNOOZED

    def stop(self) -> None:
        """
        Stop the alarm.
        """
        self.status = AlarmStatus.STOPPED
        if self.repeat == "once":
            self.enabled = False
        else:
            self.next_trigger = self._calculate_next_trigger()
            self.status = AlarmStatus.INACTIVE

    def is_ringing(self) -> bool:
        """
        Check if alarm should be ringing now.

        Returns:
            True if alarm is due and enabled
        """
        if not self.enabled:
            return False

        if self.status == AlarmStatus.SNOOZED:
            if self.snooze_until and datetime.now() >= self.snooze_until:
                self.snooze_until = None
                self.status = AlarmStatus.RINGING
                return True
            return False

        now = datetime.now()
        # Check if we're within 1 minute of trigger time
        if self.next_trigger <= now < self.next_trigger + timedelta(minutes=1):
            self.status = AlarmStatus.RINGING
            return True

        return False

    def to_dict(self) -> dict:
        """
        Convert alarm to dictionary for serialization.

        Returns:
            Dictionary representation of alarm
        """
        return {
            "id": self.id,
            "name": self.name,
            "time": self.time.isoformat(),
            "tone": self.tone,
            "repeat": self.repeat,
            "enabled": self.enabled,
            "snooze_duration": self.snooze_duration
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Alarm":
        """
        Create alarm from dictionary.

        Args:
            data: Dictionary representation of alarm

        Returns:
            Alarm instance
        """
        data["time"] = datetime.fromisoformat(data["time"])
        return cls(**data)

    def __repr__(self) -> str:
        return (
            f"Alarm(name='{self.name}', time={self.time.strftime('%H:%M')}, "
            f"tone='{self.tone}', enabled={self.enabled})"
        )
