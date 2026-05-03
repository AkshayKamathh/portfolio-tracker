# Portfolio Tracker

**Akshay K, Arsen K, Stefan L — CS122**

A web app for logging stock and crypto trades, storing them in MongoDB, and seeing what your portfolio is worth using live prices.

## What you need to install first

Your computer needs:

- **Python 3.10 or newer** — [get it here](https://www.python.org/downloads/) if you don't have it
- **Node.js 18 or newer** — [get it here](https://nodejs.org/) if you don't have it
- A **MongoDB database** — we'll set this up below (it's free)

To check if you have Python and Node already, open a terminal and type:

```bash
python --version
node --version
```

If both print a version number, you're good. Otherwise, install them first.

## MongoDB setup (1-time only)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and click **Sign Up Free**.
2. Create an account (email + password).
3. You'll see a form to "Create a deployment." Click **Create** under the free tier.
4. Wait ~1 minute for it to spin up.
5. Click **Connect** on the deployment card.
6. Choose **Drivers** (not shell or compass).
7. Select **Python** and version **4.x or higher**.
8. You'll see a connection string that looks like:  
   ```
   mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
   **Copy the entire string.** Replace `USERNAME` and `PASSWORD` with whatever you set up (or create Database Access credentials now if you haven't).

Keep this string handy — you'll paste it in the next step.

## Backend setup

Open a terminal in the **project root** (the folder that contains both `backend` and `frontend`), then run:

```bash
cd backend
```

Now create a Python virtual environment (this is a sandbox for this project's code):

```bash
python -m venv venv
```

Activate it (this changes how your terminal runs Python for this project):

```bash
source venv/bin/activate
```

**Windows users:** instead use `venv\Scripts\activate` above.

You should see `(venv)` at the start of your terminal line now.

Install the project's Python packages:

```bash
pip install -r requirements.txt
```

Wait a minute or two — it will download and install everything.

Copy the example environment file:

```bash
cp ../.env.example .env
```

Now open the file `backend/.env` in a text editor (VS Code, Notepad, whatever). You'll see:

```
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-host>/?retryWrites=true&w=majority
MONGO_DB_NAME=portfolio_tracker
FRONTEND_ORIGIN=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
YF_CACHE_TTL=60
```

Replace the `MONGO_URI=...` line with the connection string you copied from MongoDB. It should look like:

```
MONGO_URI=mongodb+srv://myuser:mypassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

Save the file.

Now start the backend server (leave this terminal open):

```bash
uvicorn app.main:app --reload
```

Wait 3–5 seconds. You should see:

```
Uvicorn running on http://127.0.0.1:8000
```

If you see that, the backend is working. **Keep this terminal running.**

## Frontend setup

Open a **second terminal** in the project root, then run:

```bash
cd frontend
npm install
```

Wait 1–2 minutes for npm to download packages.

Start the frontend:

```bash
npm run dev
```

You should see:

```
  ➜  Local:   http://localhost:5173/
```

Copy and paste that URL into your browser (or click it if your terminal is clickable).

The app should load. If you see a page that says "Portfolio Tracker," you're in.

## Checking it works

- The backend is at http://127.0.0.1:8000 in your browser (shows API docs if you visit).
- The frontend is at http://localhost:5173.
- Both terminals should stay running while you use the app.
- Click **Load demo data** in the app to see sample trades and charts.

## Stopping

When you're done:

- Press **Ctrl+C** in the backend terminal to stop the server.
- Press **Ctrl+C** in the frontend terminal to stop the dev server.

## Dependencies

- Python packages are listed in [`backend/requirements.txt`](backend/requirements.txt) (installed by `pip install -r requirements.txt`).
- JavaScript packages are listed in [`frontend/package.json`](frontend/package.json) (installed by `npm install`).

## If something breaks

**"ModuleNotFoundError" when running the backend:**  
Make sure you ran `pip install -r requirements.txt` after activating the venv.

**"Failed to fetch" error in the app:**  
Check that the backend terminal is still running and hasn't crashed. Check the backend terminal for error messages.

**Can't connect to MongoDB:**  
Double-check your connection string in `backend/.env`. Make sure it has your real username and password (not `<username>` and `<password>`).

**Port already in use:**  
If port 8000 or 5173 is taken by another app, you can change them. Backend uses port 8000 by default; frontend uses 5173 by default. Let us know if this is a problem.
