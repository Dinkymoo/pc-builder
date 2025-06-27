# FastAPI Backend for PC Builder UI

## Setup

1. Create a virtual environment (optional but recommended):
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the server:
   ```sh
   uvicorn main:app --reload
   ```

## Endpoints
- `GET /parts` — List all parts
- `GET /parts/{part_id}` — Get a single part by ID

CORS is enabled for local development.
## Creating a New Repository

To create a new Git repository for this project:

1. Initialize the repository:
   ```sh
   git init
   ```
2. Add all files:
   ```sh
   git add .
   ```
3. Commit your changes:
   ```sh
   git commit -m "Initial commit"
   ```
4. (Optional) Create a new repository on GitHub and add it as a remote:
   ```sh
   git remote add origin https://github.com/your-username/your-repo-name.git
   git push -u origin main
   ```


   # To create a Python virtual environment, run the following command in your terminal:
# python3 -m venv venv

# To activate the virtual environment on macOS/Linux:
# source venv/bin/activate

# On Windows:
# venv\Scripts\activate