
# Random User Data Pipeline 🚀

This project is a data pipeline designed to fetch user data from the [Random User API](https://randomuser.me/), transform and clean the data, and store it in a PostgreSQL database. It uses asynchronous requests to efficiently collect 150 user records and supports checkpointing to handle interruptions. Additionally, it includes exploratory data analysis (EDA) and visualizations. 📊

## Features

- **Asynchronous Data Collection:** Fetches 150 user records from the Random User API using asynchronous requests with `asyncio` and `aiohttp`. ⏱️
- **Checkpointing:** The pipeline saves the index of the last successful API call, allowing it to resume from where it left off in case of interruption. 🔄
- **Data Transformation:** Extracts and flattens JSON data, computes derived values like age, and converts timezone offsets into minutes. 🛠️
- **PostgreSQL Integration:** Stores the user data in a PostgreSQL database. 🗄️
- **Exploratory Data Analysis:** Computes key statistics such as average age, gender distribution, and user counts by country, and visualizes them. 🌍

## Getting Started 💻

### Prerequisites

Before running the pipeline, ensure that you have the following:

- Python 3.7 or higher
- PostgreSQL database installed and running
- Necessary Python libraries:
  ```bash
  pip install requests psycopg2 pandas matplotlib
  ```

### Setup

1. **Create PostgreSQL Database:**
   - Create a PostgreSQL database called `assessment` on your local machine.
   - Update the connection details (username, password, host, port) in the script to match your local database setup.

2. **Download the Repository:**
   - Clone this repository to your local machine.
   ```bash
   git clone https://github.com/muhammed-ziyan-ummalil/random-user-pipeline
   ```

3. **Configuration:**
   - Ensure the file `last_successful_index.txt` exists in the same directory as the script. This file tracks the progress of the API calls.

### Running the Pipeline 🚀

1. **Run the Pipeline:**
   - Execute the script to start the data collection and ETL process.
   ```bash
   python data_pipeline.py
   ```

2. **Exploratory Data Analysis (EDA):**
   - After the data is collected, the script will perform EDA on the user data and display visualizations for:
     - **Average Age**
     - **Gender Distribution**
     - **User Counts by Country**

