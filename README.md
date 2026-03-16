# HealthPal - Innovation Challenge

HealthPal is a Streamlit-based healthcare assistant demo app built for the Synapxe Innovation Challenge.
It combines health tracking, medication management, AI-powered health chat, and a community feed using a local CSV-backed data layer.

## Features

- Home dashboard with recent vitals and trend charts
- Medication planner, reminders, and taken-status logging
- AI chat for health and nutrition guidance
- Food image analysis (Gemini)
- Community posts and basic engagement (like/post)
- Bilingual UI support (English and Chinese)

## Project Structure

```text
Innovation-Challenge/
	healthpal_app.py          # Streamlit app entry
	data_layer.py             # CSV data layer and business logic
	requirements.txt          # Python dependencies
	secrets.toml              # Local API keys (not for production)
	data/                     # CSV data files
```

## Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- OpenAI-compatible client (for MERaLiON endpoint)
- Google Gemini SDK (for image analysis)

## Quick Start

### 1. Clone repository

```bash
git clone https://github.com/bbbbronya/Innovation-Challenge
cd Innovation-Challenge
```

### 2. Create and activate virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Optional but recommended (used by image analysis path):

```bash
pip install google-genai toml
```

### 4. Configure API keys

Create or update `secrets.toml` in the project root:

```toml
merlion_API_KEY = "your_meralion_key"
gemini_API_KEY = "your_gemini_key"
```

Notes:

- AI-related features can be accessed directly via the [deployed link](https://healthpal-v1.streamlit.app/). To run locally, you'll need to add your API_KEY to `secrets.toml` manually.

### 5. Run app

```bash
streamlit run healthpal_app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Data Layer

The app uses CSV files under `data/` as a lightweight local database. On startup, `ensure_data_exists()` seeds missing files automatically.

Main files include:

- `users.csv`
- `vitals.csv`
- `medications.csv`
- `med_logs.csv`
- `medication_plan.csv`
- `medication_logs.csv`
- `lab_results.csv`
- `community_posts.csv`



