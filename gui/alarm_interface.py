"""
GUI interface for the Alarm Clock application using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional

from core.alarm_manager import AlarmManager
from core.alarm import Alarm
from tones.default_tones import TONES, TONE_DESCRIPTIONS


class AlarmClockGUI:
    """
    GUI for managing and displaying alarms.
    """

    def __init__(self):
        """
        Initialize the GUI.
        """
        self.root = tk.Tk()
        self.root.title("⏰ Alarm Clock")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.manager = AlarmManager()
        self.manager.register_alarm_callback(self._on_alarm_triggered)
        self.manager.register_stop_callback(self._on_alarm_stopped)
        self.manager.start()

        self.alarm_widgets = {}  # Track alarm UI elements
        self.currently_ringing = None  # Track ringing alarm

        self._setup_ui()
        self._update_alarm_list()

    def _setup_ui(self) -> None:
        """
        Set up the user interface.
        """
        # Title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(
            title_frame,
            text="⏰ Alarm Clock Manager",
            font=("Arial", 18, "bold")
        ).pack(side=tk.LEFT)

        # Create New Alarm Section
        self._create_input_section()

        # Alarms List Section
        self._create_alarms_list_section()

        # Footer
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(
            footer_frame,
            text="Clear All Inactive",
            command=self._clear_inactive_alarms
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            footer_frame,
            text="Exit",
            command=self._on_close
        ).pack(side=tk.RIGHT, padx=5)

    def _create_input_section(self) -> None:
        """
        Create the section for creating new alarms.
        """
        input_frame = ttk.LabelFrame(self.root, text="Create New Alarm", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # Name
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.name_entry.insert(0, "My Alarm")

        # Time
        ttk.Label(input_frame, text="Time (HH:MM):").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.time_entry = ttk.Entry(input_frame, width=10)
        self.time_entry.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=5)
        now = datetime.now()
        self.time_entry.insert(0, (now + timedelta(minutes=1)).strftime("%H:%M"))

        # Tone
        ttk.Label(input_frame, text="Tone:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tone_var = tk.StringVar(value="digital")
        tone_combo = ttk.Combobox(
            input_frame,
            textvariable=self.tone_var,
            values=list(TONES.keys()),
            state="readonly",
            width=27
        )
        tone_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

        # Repeat
        ttk.Label(input_frame, text="Repeat:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.repeat_var = tk.StringVar(value="once")
        repeat_combo = ttk.Combobox(
            input_frame,
            textvariable=self.repeat_var,
            values=["once", "daily", "weekdays"],
            state="readonly",
            width=7
        )
        repeat_combo.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=5)

        # Snooze Duration
        ttk.Label(input_frame, text="Snooze (min):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.snooze_var = tk.StringVar(value="5")
        snooze_combo = ttk.Combobox(
            input_frame,
            textvariable=self.snooze_var,
            values=["5", "10", "15", "20"],
            state="readonly",
            width=27
        )
        snooze_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        # Create Button
        ttk.Button(
            input_frame,
            text="Create Alarm",
            command=self._create_alarm
        ).grid(row=2, column=2, columnspan=2, sticky=tk.EW, padx=5, pady=5)

        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

    def _create_alarms_list_section(self) -> None:
        """
        Create the section displaying all alarms.
        """
        list_frame = ttk.LabelFrame(self.root, text="Active Alarms", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox
        self.alarm_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            height=12
        )
        self.alarm_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.alarm_listbox.yview)

        # Control Frame
        control_frame = ttk.Frame(list_frame)
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            control_frame,
            text="🔊 Edit",
            command=self._edit_selected_alarm
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="🗑️  Delete",
            command=self._delete_selected_alarm
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="⏸️  Disable",
            command=self._disable_selected_alarm
        ).pack(side=tk.LEFT, padx=5)

    def _create_alarm(self) -> None:
        """
        Create a new alarm from input fields.
        """
        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a name")
                return

            time_str = self.time_entry.get().strip()
            try:
                time_obj = datetime.strptime(time_str, "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Time must be in HH:MM format")
                return

            tone = self.tone_var.get()
            repeat = self.repeat_var.get()
            snooze_duration = int(self.snooze_var.get())

            alarm = Alarm(
                name=name,
                time=time_obj,
                tone=tone,
                repeat=repeat,
                snooze_duration=snooze_duration
            )

            self.manager.add_alarm(alarm)
            messagebox.showinfo("Success", f"Alarm '{name}' created!")
            self._update_alarm_list()
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, "My Alarm")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create alarm: {str(e)}")

    def _update_alarm_list(self) -> None:
        """
        Update the display of all alarms.
        """
        self.alarm_listbox.delete(0, tk.END)
        alarms = self.manager.get_all_alarms()

        for alarm in alarms:
            status = "✓" if alarm.enabled else "✗"
            time_str = alarm.time.strftime("%H:%M")
            display_text = f"{status} {alarm.name} @ {time_str} ({alarm.tone}) [{alarm.repeat}]"
            self.alarm_listbox.insert(tk.END, display_text)
            self.alarm_widgets[self.alarm_listbox.size() - 1] = alarm

    def _delete_selected_alarm(self) -> None:
        """
        Delete the selected alarm.
        """
        selection = self.alarm_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alarm")
            return

        index = selection[0]
        alarm = self.alarm_widgets.get(index)
        if alarm:
            self.manager.remove_alarm(alarm.id)
            self._update_alarm_list()
            messagebox.showinfo("Success", f"Alarm '{alarm.name}' deleted!")

    def _disable_selected_alarm(self) -> None:
        """
        Toggle enable/disable for selected alarm.
        """
        selection = self.alarm_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alarm")
            return

        index = selection[0]
        alarm = self.alarm_widgets.get(index)
        if alarm:
            alarm.enabled = not alarm.enabled
            self.manager.update_alarm(alarm)
            self._update_alarm_list()
            status = "enabled" if alarm.enabled else "disabled"
            messagebox.showinfo("Success", f"Alarm '{alarm.name}' {status}!")

    def _edit_selected_alarm(self) -> None:
        """
        Open edit dialog for selected alarm.
        """
        selection = self.alarm_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alarm")
            return

        index = selection[0]
        alarm = self.alarm_widgets.get(index)
        if alarm:
            self._show_edit_dialog(alarm)

    def _show_edit_dialog(self, alarm: Alarm) -> None:
        """
        Show dialog to edit alarm properties.
        """
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Alarm - {alarm.name}")
        edit_window.geometry("400x300")

        # Name
        ttk.Label(edit_window, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=10)
        name_entry.insert(0, alarm.name)

        # Time
        ttk.Label(edit_window, text="Time (HH:MM):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        time_entry = ttk.Entry(edit_window, width=30)
        time_entry.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=10)
        time_entry.insert(0, alarm.time.strftime("%H:%M"))

        # Tone
        ttk.Label(edit_window, text="Tone:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        tone_var = tk.StringVar(value=alarm.tone)
        tone_combo = ttk.Combobox(
            edit_window,
            textvariable=tone_var,
            values=list(TONES.keys()),
            state="readonly"
        )
        tone_combo.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=10)

        # Snooze Duration
        ttk.Label(edit_window, text="Snooze (min):").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        snooze_var = tk.StringVar(value=str(alarm.snooze_duration))
        snooze_combo = ttk.Combobox(
            edit_window,
            textvariable=snooze_var,
            values=["5", "10", "15", "20"],
            state="readonly"
        )
        snooze_combo.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=10)

        def save_changes():
            try:
                alarm.name = name_entry.get().strip()
                time_str = time_entry.get().strip()
                alarm.time = datetime.strptime(time_str, "%H:%M")
                alarm.tone = tone_var.get()
                alarm.snooze_duration = int(snooze_var.get())
                self.manager.update_alarm(alarm)
                self._update_alarm_list()
                messagebox.showinfo("Success", "Alarm updated!")
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input")

        ttk.Button(
            edit_window,
            text="Save",
            command=save_changes
        ).grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=20)

        edit_window.columnconfigure(1, weight=1)

    def _clear_inactive_alarms(self) -> None:
        """
        Remove all inactive alarms.
        """
        alarms_to_remove = [
            alarm for alarm in self.manager.get_all_alarms()
            if not alarm.enabled
        ]
        for alarm in alarms_to_remove:
            self.manager.remove_alarm(alarm.id)

        if alarms_to_remove:
            self._update_alarm_list()
            messagebox.showinfo("Success", f"Removed {len(alarms_to_remove)} inactive alarm(s)")
        else:
            messagebox.showinfo("Info", "No inactive alarms to clear")

    def _on_alarm_triggered(self, alarm: Alarm) -> None:
        """
        Called when an alarm triggers.
        """
        self.currently_ringing = alarm
        response = messagebox.showwarning(
            "⏰ ALARM!",
            f"{alarm.name}\n\nSnooze or Stop?",
            type=messagebox.RETRYCANCEL
        )

        if response == messagebox.RETRY:
            self.manager.snooze_alarm(alarm.id)
        else:
            self.manager.stop_alarm(alarm.id)

        self.currently_ringing = None
        self._update_alarm_list()

    def _on_alarm_stopped(self, alarm: Alarm) -> None:
        """
        Called when an alarm is stopped.
        """
        self._update_alarm_list()

    def _on_close(self) -> None:
        """
        Handle window close.
        """
        self.manager.stop()
        self.root.destroy()

    def run(self) -> None:
        """
        Start the GUI event loop.
        """
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()
