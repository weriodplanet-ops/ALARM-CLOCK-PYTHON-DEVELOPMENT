#!/usr/bin/env python3
"""
Main entry point for the Alarm Clock application.
"""

import sys
from gui.alarm_interface import AlarmClockGUI


def main():
    """
    Start the Alarm Clock application.
    """
    app = AlarmClockGUI()
    app.run()


if __name__ == "__main__":
    main()
