# kmbase

# Project Setup and Configuration

## Prerequisites

- Anaconda or Miniconda
- PostgreSQL server

## Detailed Setup Instructions

### 1. Clone the Repository

```
git clone [your-repo-url]
cd [your-project-directory]
```

### 2. Set Up Anaconda Environment

1. Install Anaconda or Miniconda if not already installed.
2. Open a terminal or Anaconda prompt.
3. Navigate to your project directory.
4. Create the environment from the YAML file:
   ```
   conda env create -f environment.yaml
   ```
5. Activate the environment:
   ```
   conda activate kmbase
   ```

### 3. Configure PostgreSQL

1. Install PostgreSQL if not already installed.
2. Start the PostgreSQL service.
3. Create a new database for the project:
   ```
   psql -U postgres
   CREATE DATABASE kbase;
   \q
   ```
4. Update the database connection settings in your project's configuration file config/config.yml

### 4. Configure Minio

1. Download Minio server for your operating system from the official website.
2. Place the Minio executable in a convenient location .
3. Create a data directory for Minio (e.g., C:\Users\Mouad\Desktop\kM\Data).
4. Start Minio server:
   ```
   C:\minio.exe server "C:\Users\Mouad\Desktop\kM\Data" --console-address ":9001"
   ```
5. Open the Minio Console in a web browser (default: http://127.0.0.1:9001).
6. Create a new bucket for the project:
   - Click on "Create Bucket" and enter a name for your bucket (kmbase).
7. Create a user with read and write roles:
   - Go to "Identity" > "Users" > "Create User"
   - Set a username and password (kmbase:kmbasepass)
   - Assign read and write policies to the user for the created bucket
8. Set up a webhook for Minio bucket events:
   - Go to "Buckets" > [Your Bucket] > "Events"
   - Click "Add New Event Notification"
   - Configure the event types and specify the endpoint URL for your webhook

## Running the Application


1. Start the Minio server:
   ```
   C:\minio.exe server "C:\Users\Mouad\Desktop\kM\Data" --console-address ":9001"
   ```
Ensure you're in the project's root directory and the Conda environment is activated. Run each command in a separate terminal window or tab.

2. Run the API server for interacting with postgres database:
   ```
   cd .\API\
   flask run
   ```

3. Run the Streamlit application:
   ```
   streamlit run main.py --server.headless true
   ```

4. Run the Assistant:
   ```
   cd .\Assistant\
   uvicorn main:app
   ```