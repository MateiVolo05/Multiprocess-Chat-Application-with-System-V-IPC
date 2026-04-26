# Multiprocess Chat Application with System-V IPC
## Advanced Inter-Process Communication & Relational Data Management

## 📌 Project Overview
This project is a sophisticated multiprocess chat system that enables real-time communication between multiple authenticated users. It leverages **Unix System-V Message Queues** for efficient, asynchronous inter-process communication (IPC) and uses **SQLite** for robust persistent storage of user accounts and message history.

## ⚙️ Key Technical Features
* **IPC with JSON Payloads:** Messages are serialized as JSON objects and routed through System-V message queues. The system uses the unique `userId` as the message `type` for precise routing between processes.
* **Relational Database Schema:** A structured SQLite database manages two core entities: `ACCOUNTS` (user credentials and profiles) and `MESSAGES` (persistent chat history with timestamps).
* **Threaded Communication Layer:** Implements a specialized `CommunicationsManager` using `QThread` to listen for incoming messages in the background, preventing UI freezes during heavy I/O operations.
* **Full Authentication Flow:** Includes a complete Login and Registration system with input validation and error handling (e.g., detecting existing users or wrong credentials).
* **Modern UI/UX:** Features a polished PyQt5 interface with rich-text chat bubbles, automated scrolling, and dynamic date separators for organized message history.

## 📊 System Design
The application is built on a modular architecture to separate concerns:
* **Database Layer:** Handles all CRUD operations for users and messages.
* **Communication Layer:** Manages the low-level `sysv_ipc` operations, including message serialization and background listening.
* **UI Layer:** Handles user interaction and transitions from the Login screen to the Chat interface.

## 🛠 Project Structure
* `main.py`: Orchestrates the application flow and UI logic.
* `CommunicationsManager.py`: Handles the background IPC thread and message routing.
* `DatabaseManager.py`: Encapsulates all SQL logic for persistent storage.
* `*.ui` files: XML-based interface definitions (Login and Main Chat windows).

## 🔧 Tools & Technologies
* **Language:** Python 3
* **GUI Framework:** PyQt5
* **IPC Mechanism:** System-V Message Queues (`sysv_ipc`)
* **Data Serialization:** JSON
* **Database:** SQLite3

## 🚀 Setup & Execution
1. **Prerequisites:** A Linux environment is required for System-V IPC support.
2. **Install Dependencies:**
   ```bash
   pip install PyQt5 sysv_ipc
