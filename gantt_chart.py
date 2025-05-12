import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Project timeline
start_date = datetime(2025, 3, 28)
end_date = datetime(2025, 5, 8)

# Tasks mapped to SDLC phases (feature-related)
tasks = [
    # Planning
    {"phase": "Planning", "task": "Project setup", "start": datetime(2025, 3, 28), "duration": 3},
    # Requirements Analysis
    {"phase": "Requirements Analysis", "task": "Define features", "start": datetime(2025, 3, 30), "duration": 3},
    # Design
    {"phase": "Design", "task": "UI and database design", "start": datetime(2025, 4, 1), "duration": 4},
    # Implementation
    {"phase": "Implementation", "task": "User authentication", "start": datetime(2025, 4, 2), "duration": 4},
    {"phase": "Implementation", "task": "Event management", "start": datetime(2025, 4, 5), "duration": 4},
    {"phase": "Implementation", "task": "Task management", "start": datetime(2025, 4, 8), "duration": 4},
    {"phase": "Implementation", "task": "Guest management", "start": datetime(2025, 4, 11), "duration": 4},
    {"phase": "Implementation", "task": "Fullscreen and UI", "start": datetime(2025, 4, 14), "duration": 3},
    {"phase": "Implementation", "task": "Export functionality", "start": datetime(2025, 4, 16), "duration": 3},
    {"phase": "Implementation", "task": "Backup and recovery", "start": datetime(2025, 4, 18), "duration": 3},
    # Testing
    {"phase": "Testing", "task": "Unit and integration tests", "start": datetime(2025, 4, 15), "duration": 17},
    # Deployment
    {"phase": "Deployment", "task": "Staging deployment", "start": datetime(2025, 5, 2), "duration": 3},
    # Maintenance
    {"phase": "Maintenance", "task": "Bug fixes and documentation", "start": datetime(2025, 5, 5), "duration": 4},
]

# Colors for phases
phase_colors = {
    "Planning": "skyblue",
    "Requirements Analysis": "lightgreen",
    "Design": "lightcoral",
    "Implementation": "gold",
    "Testing": "violet",
    "Deployment": "orange",
    "Maintenance": "lightgrey"
}

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))

# Plot tasks
for i, task in enumerate(tasks):
    start = mdates.date2num(task["start"])
    duration = task["duration"]
    ax.barh(i, duration, left=start, height=0.4, color=phase_colors[task["phase"]], edgecolor="black")
    ax.text(start + duration / 2, i, task["task"], ha="center", va="center", fontsize=9)

# Format x-axis (dates)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
plt.xticks(rotation=45)
ax.set_xlim(mdates.date2num(start_date), mdates.date2num(end_date + timedelta(days=1)))

# Format y-axis (tasks)
ax.set_yticks(range(len(tasks)))
ax.set_yticklabels([task["task"] for task in tasks])
ax.invert_yaxis()

# Add grid and labels
ax.grid(True, linestyle="--", alpha=0.7)
ax.set_xlabel("Date")
ax.set_ylabel("Tasks")
ax.set_title("Event Planner App SDLC Gantt Chart (Mar 28 - May 8, 2025)")

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, edgecolor="black", label=phase) for phase, color in phase_colors.items()]
ax.legend(handles=legend_elements, loc="upper right")

# Save
plt.tight_layout()
plt.savefig("gantt_chart.png")
plt.close()