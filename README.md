# ConstructLinkBot

## Project Overview

ConstructLinkBot is a Telegram bot designed for construction companies to facilitate and manage the supply and demand processes in construction projects. This project leverages Telegram's API, database interactions, and robust back-end processing to streamline user experiences and operational efficiency.

## Project Structure

The project has the following structure:

```
constructlinkbot/
├── core/
│   ├── requirements.txt
│   ├── sql_mg.py
│   └── Telegram.py
└── README.md
```

## Explanation of Core Files

### 1. sql_mg.py

- **Purpose**: Manages the database connections and operations needed for storing and retrieving project data.
- **Main Libraries**: `mysql-connector-python`
- **Functionality**: Establishes connections to the SQL database, executes queries, and handles data management tasks.

### 2. Telegram.py

- **Purpose**: Contains the main logic for the Telegram bot's interactions and functionalities.
- **Main Libraries**: `pyTelegramBotAPI`
- **Functionality**: Handles bot commands, processes user messages, and manages user interactions on Telegram.

## Installation and Setup

### Prerequisites

- Python 3.x (recommended: Python 3.8 or higher)
- A Telegram bot token from the [Telegram BotFather](https://core.telegram.org/bots#botfather)

### Installation Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ramtin099/constructlinkbot.git
   cd constructlinkbot/core
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Required Modules

The project relies on the following Python modules:

- `certifi==2024.8.30`
- `charset-normalizer==3.3.2`
- `idna==3.10`
- `mysql-connector-python==9.0.0`
- `pillow==10.4.0`
- `pyTelegramBotAPI==4.23.0`
- `requests==2.32.3`
- `urllib3==2.2.3`

## How to Use the Project

To start the bot, run the `Telegram.py` script:

```bash
python Telegram.py
```

Ensure that your Telegram bot token is correctly set up within the code before running it.

## Additional Notes

- The bot can be customized further by updating command logic or adding new features as needed.
