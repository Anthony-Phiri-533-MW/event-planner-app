# Event Planner User Manual(With source code)

## Introduction

The **Event Planner** is a desktop application for managing events, tasks, and guest lists. Built with Python and PyQt5, it provides an intuitive interface for users to sign up, log in, create events, add tasks and guests, and export event data. This manual guides you through installing, running, and using the application.

## System Requirements

- **Operating System**: Linux (tested on Ubuntu), Windows, or macOS.
- **Disk Space**: \~100 MB for the executable or \~500 MB for the source code with dependencies.
- **Dependencies** (for source code):
  - Python 3.8+
  - PyQt5
  - requests
- No internet connection required after setup.

## Installation

### Option 1: Using the Executable

1. **Download the Executable**:

   - Obtain `EventPlanner` (Linux/macOS) or `EventPlanner.exe` (Windows) from the provided distribution.
   - Place it in a writable directory (e.g., `~/EventPlanner`).

2. **Run the Executable**:

   - **Linux/macOS**:

     ```bash
     cd ~/EventPlanner
     chmod +x EventPlanner
     ./EventPlanner
     ```
   - **Windows**:
     - Double-click `EventPlanner.exe` or run via Command Prompt:

       ```cmd
       cd %USERPROFILE%\EventPlanner
       EventPlanner.exe
       ```

### Option 2: Using Source Code

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/username/event-planner-app.git
   cd event-planner-app
   ```

2. **Set Up Virtual Environment**:

   ```bash
   python3 -m venv .
   source bin/activate  # Linux/macOS
   .\Scripts\activate   # Windows
   ```

3. **Install Dependencies**:

   ```bash
   pip install PyQt5 requests
   ```

4. **Run the Application**:

   - Use the provided `run.sh` script (Linux/macOS):

     ```bash
     chmod +x run.sh
     ./run.sh
     ```
   - Or run directly:

     ```bash
     python -m event_planner.main
     ```

## Getting Started

Upon launching, the application opens a **Login Window**. New users must sign up, while returning users can log in.

### 1. Sign Up

1. **Open Signup**:
   - In the Login Window, click **Signup** or the signup link.
2. **Enter Details**:
   - **Username**: Choose a unique username (e.g., `john_doe`).
   - **Password**: Enter a secure password (at least 6 characters).
   - **Confirm Password**: Re-enter the password.
3. **Submit**:
   - Click **Signup**.
   - If successful, a message confirms account creation, and you’re redirected to the Login Window.
   - If the username exists or passwords don’t match, an error message appears.

### 2. Log In

1. **Enter Credentials**:
   - In the Login Window, enter your **Username** and **Password**.
2. **Log In**:
   - Click **Login**.
   - If credentials are correct, the **Main Window** opens, showing your events.
   - If incorrect, an error message prompts you to try again or sign up.

### 3. Create an Event

1. **Access the Main Window**:
   - After logging in, you’re in the Main Window with a table of events.
2. **Add Event**:
   - Click the **Add Event** button or select **Add Event** from the menu.
3. **Fill Event Details**:
   - In the Event Dialog:
     - **Name**: Enter the event name (e.g., `Birthday Party`).
     - **Date**: Select the date using the calendar widget.
     - **Time**: Choose the time.
     - **Location**: Enter the location (e.g., `Community Hall`).
     - **Description**: Add details (optional).
4. **Save**:
   - Click **OK** to save the event.
   - The event appears in the Main Window’s table.

### 4. Manage Tasks

1. **Select an Event**:
   - Double-click an event in the Main Window’s table to open the **Event Details Dialog**.
2. **Add Task**:
   - In the Tasks tab, click **Add Task**.
   - Enter:
     - **Task Name**: E.g., `Book Venue`.
     - **Due Date**: Select a date.
     - **Status**: Choose `Pending`, `In Progress`, or `Completed`.
3. **Save Task**:
   - Click **OK** to add the task to the event.
4. **Edit/Delete Task**:
   - Select a task in the Tasks table.
   - Click **Edit Task** to modify or **Delete Task** to remove.

### 5. Manage Guests

1. **Access Guests**:
   - In the Event Details Dialog, go to the Guests tab.
2. **Add Guest**:
   - Click **Add Guest**.
   - Enter:
     - **Name**: E.g., `Jane Smith`.
     - **Contact**: E.g., `jane@example.com` or phone number.
     - **Status**: Choose `Invited`, `Confirmed`, or `Declined`.
3. **Save Guest**:
   - Click **OK** to add the guest.
4. **Edit/Delete Guest**:
   - Select a guest in the Guests table.
   - Click **Edit Guest** to modify or **Delete Guest** to remove.

### 6. Toggle Fullscreen

1. **Enter Fullscreen**:
   - Click the **Fullscreen** button or select **View &gt; Fullscreen** from the menu.
   - The app expands to fill the screen.
2. **Exit Fullscreen**:
   - Press **Esc** or click **Fullscreen** again.

### 7. Export Event Data

1. **Access Export**:
   - In the Main Window, select **File &gt; Export** from the menu.
2. **Choose Format**:
   - Select **CSV** or another supported format (if implemented).
3. **Save File**:
   - Choose a location and filename (e.g., `events.csv`).
   - The file includes event details, tasks, and guests.

### 8. Log Out

1. **Log Out**:
   - Click **File &gt; Logout** from the menu.
   - You’re returned to the Login Window.

## Troubleshooting

- **Login Fails**:
  - Ensure username and password are correct. Use the signup link if you don’t have an account.
- **App Doesn’t Start**:
  - **Executable**: Ensure it’s in a writable directory. Run from a terminal to see errors.
  - **Source Code**: Verify dependencies (`pip install PyQt5 requests`) and use `./run.sh`.
- **QStandardPaths Warning** (Linux):
  - Should be resolved by `run.sh`. If not, contact support.
- **Contact Support**:
  - Email `support@example.com` or check the GitHub repository for issues.

## Tips

- Save events frequently to avoid data loss.
- Use descriptive names for events and tasks to stay organized.
- Export data regularly to back up your plans.