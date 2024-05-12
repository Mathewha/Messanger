# Messanger
# Chat Application (Client and Server)

This project implements a holistic chat application consisting of a GUI frontend desktop app and a backend server app. These are two separate applications but part of a single project with two main functions. The main goal is to facilitate communication between users via a client-server architecture.

## Features

### GUI Client App
- Connect to the server with identity (e.g., name, nickname) and pre-knowledge about the server address (IP:PORT).
- Display list of connected users and number of messages exchanged with each.
- Refresh list of users.
- Select a user to view chat history (messages with annotations to/from and date & time) and send new messages.
- Receive messages from other users.
- Search for messages by text.
- Optional: Real-time statistics refresh, real-time message refresh, disconnect from server, separate chats with tabs.

### Server App
- Listen for connections on a specific port.
- Maintain a list of connected clients with their identities.
- Handle commands sent by the GUI app (e.g., send message, get users list, get statistics, find message by text, get message history with specific user).
- Use an in-memory database to store message and user information.
- Optional: Run server app in a Docker container, perform stress tests simulating multiple users simultaneously.

## Issues and Considerations
- Design structure of classes/interfaces, especially on the server side.
- Design an app layer protocol for communication between GUI app and server.
- Implement real-time functionality without blocking the GUI.
- Handle parallel access to the database structure (e.g., concurrent search and message sending).

