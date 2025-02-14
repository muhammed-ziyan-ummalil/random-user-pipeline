import requests
import time
import json
import os
import psycopg2
from datetime import datetime
import pandas as pd

URL = "https://randomuser.me/api/"
MAX_RETRIES = 5
DELAY = 5  # seconds
INDEX_FILE = "last_successful_index.txt"

def read_last_index():
    # Read the last successful index from the file
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as file:
            return int(file.read().strip())
    return -1

def write_last_index(index):
    # Write the last successful index to the file
    with open(INDEX_FILE, "w") as file:
        file.write(str(index))

def fetch_user_data():
    # Fetch user data from the API with retry mechanism
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(URL)
            return response.json()['results'][0]
        except requests.exceptions.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(DELAY)
    return None

def convert_timezone_offset(offset):
    # Convert timezone offset string to minutes
    sign = 1 if offset[0] == '+' else -1
    if offset[1:]:  # Check if offset is not empty
        try:
            hours, minutes = map(int, offset[1:].split(':'))
        except ValueError:
            return 0  # Default to 0 if conversion fails
        return sign * (hours * 60 + minutes)
    return 0  # Default to 0 if offset is empty

def extract_user_info(data):
    # Extract and transform user information from the API response
    dob = datetime.strptime(data['dob']['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    timezone_offset = convert_timezone_offset(data['location']['timezone']['offset'])
    
    # Reversing the username
    reversed_username = data['login']['username'][::-1]
    
    # Caesar cipher shift (by 2) to transform password
    password = data['login']['password']
    transformed_password = password[-2:] + password[:-2] if len(password) > 2 else password

    # Concatenating reversed username and transformed password
    hash_user = reversed_username + transformed_password

    return {
        "Full Name": f"{data['name']['first']} {data['name']['last']}",
        "Gender": data['gender'],
        "Email": data['email'],
        "Date of Birth": dob.isoformat(),
        "Age": datetime.now().year - dob.year - ((datetime.now().month, datetime.now().day) < (dob.month, dob.day)),
        "City": data['location']['city'],
        "State": data['location']['state'],
        "Country": data['location']['country'],
        "Phone": data['phone'],
        "Nationality": data['nat'],
        "Timezone Offset": timezone_offset,
        "Username": data['login']['username'],
        "Password": data['login']['password'],
        "Hash User": hash_user  # New field with reversed username and transformed password
    }

def create_table_if_not_exists(conn):
    # Create the table if it does not exist
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS random_users (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(255),
                gender VARCHAR(50),
                email VARCHAR(255),
                dob TIMESTAMP,
                age INTEGER,
                city VARCHAR(255),
                state VARCHAR(255),
                country VARCHAR(255),
                phone VARCHAR(50),
                nationality VARCHAR(50)
            )
        """)
        conn.commit()

def insert_user_info(conn, user_info):
    # Insert user information into the database
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO random_users (full_name, gender, email, dob, age, city, state, country, phone, nationality)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_info["Full Name"],
            user_info["Gender"],
            user_info["Email"],
            user_info["Date of Birth"],
            user_info["Age"],
            user_info["City"],
            user_info["State"],
            user_info["Country"],
            user_info["Phone"],
            user_info["Nationality"]
        ))

def main():
    global responses
    last_index = read_last_index()

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname="assessment",
        user="postgres",
        password="1234",
        host="localhost",
        port=5432  
    )

    try:
        create_table_if_not_exists(conn)
        
        for i in range(last_index + 1, last_index + 151):
            data = fetch_user_data()
            if data:
                user_info = extract_user_info(data)
                insert_user_info(conn, user_info)
                responses.append(user_info)
                write_last_index(i)
            print(f"Fetching data {i + 1}...")

        conn.commit()
    finally:
        conn.close()

responses = []

if __name__ == "__main__":
    main()
    import matplotlib.pyplot as plt

    def compute_statistics(responses):
        # Compute statistics from the collected user data
        df = pd.DataFrame(responses)
        
        # Compute the average user age
        average_age = df['Age'].mean()
        
        # Determine the distribution of genders
        gender_distribution = df['Gender'].value_counts().to_dict()
        
        # Count the number of users by country
        country_counts = df['Country'].value_counts().to_dict()
        
        return average_age, gender_distribution, country_counts

    def plot_user_counts_by_country(country_counts):
        # Plot the number of users by country
        countries = list(country_counts.keys())
        counts = list(country_counts.values())
        
        plt.figure(figsize=(10, 6))
        plt.bar(countries, counts, color='skyblue')
        plt.xlabel('Country')
        plt.ylabel('Number of Users')
        plt.title('User Counts per Country')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

    # Compute statistics
    average_age, gender_distribution, country_counts = compute_statistics(responses)
    
    # Print statistics
    print(f"Average Age: {average_age}")
    print(f"Gender Distribution: {gender_distribution}")
    print(f"User Counts by Country: {country_counts}")
    
    # Plot user counts by country
    plot_user_counts_by_country(country_counts)
