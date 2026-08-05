# farmer-voice-agent

## Run the text chat UI

1. Start the backend and database:

```bash
docker compose up --build
```

2. In a second terminal, install the Python dependencies:

```bash
python -m pip install -r app/requirements.txt
```

3. Start the Streamlit chat app:

```bash
streamlit run streamlit_app.py
```

## Run the voice demo

Open the Streamlit page and switch the demo mode to `Voice`. Record a short answer in the browser, and the app will send it to the FastAPI backend, show the transcript, and play the assistant reply back as audio.

## DBeaver connection

Connect DBeaver to PostgreSQL with these settings:

- Host: `localhost`
- Port: `5432`
- Database: `farmerdb`
- User: `postgres`
- Password: `farmerdemo`