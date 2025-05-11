# Event Planner App

An easy-to-use desktop event planner application built using Python and PyQt5. This application allows users to efficiently manage events, tasks, and schedules, providing a straightforward and user-friendly interface for organizing personal and professional events.

## Features

* **Event Management:** Create, update, and delete events.
* **Task Management:** Add tasks related to events, track progress, and manage deadlines.
* **Database Storage:** Persistent storage using a SQLite database for offline access.
* **Modular Design:** Organized code structure for easy maintenance and scalability.
* **Cross-Platform:** Compatible with Windows, macOS, and Linux.

## Prerequisites

Make sure you have the following installed:

* Python 3.10 or newer
* pip (Python package installer)

## Installation

Clone the repository and navigate to the project directory:

```bash
$ git clone https://github.com/Anthony-Phiri-533-MW/event-planner-app.git
$ cd event-planner-app
```

Create a virtual environment and install the required packages:

```bash
$ python -m venv venv
$ source venv/bin/activate  # On Windows use `venv\Scripts\activate`
$ pip install -r requirements.txt
```

## Running the Application

To run the application, use the provided shell script:

```bash
$ ./run.sh
```

## Project Structure

```
.
├── event_planner/         # Main application logic
│   ├── app.py
│   ├── database.py
│   ├── delegates.py
│   ├── dialogs.py
│   └── main.py
├── requirements.txt       # Python dependencies
├── run.sh                 # Startup script
└── README.md              # Project documentation
```

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact

Created by Anthony Phiri - feel free to reach out!

Email: [malawi.anthonymw@outlook.com](mailto:malawi.anthonymw@outlook.com)

