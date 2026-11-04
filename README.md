# AgriPilot — Agentic AI Farm Decision Support

A Streamlit prototype for farm-level decision support. It combines separate, inspectable agents for:
- weather context (Open-Meteo public forecast),
- soil observation and soil-test review,
- crop symptom triage (not disease diagnosis),
- irrigation decision support,
- retrieval of bundled general agronomy reminders,
- supervisor-based action-plan generation,
- SQLite assessment history and JSON export.

## Important scope and safety
This is a decision-support prototype, **not** an agronomist, plant pathologist or irrigation controller. It does not prescribe pesticide products/doses, fertilizer quantities or exact irrigation volumes. Symptoms are non-specific. Confirm diagnosis and input decisions with the local Krishi Vigyan Kendra (KVK), agriculture department or qualified agronomist. Follow product labels and local regulations. Do not use the app as the sole basis for a high-stakes farm decision.

## Run locally (Windows / VS Code)
1. Install Python 3.10 or newer.
2. Extract this ZIP and open the `agri_agentic_ai` folder in VS Code.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   streamlit run app.py
   ```

6. Browser opens at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud
1. Push the extracted project folder to a GitHub repository.
2. In Streamlit Community Cloud, choose **New app**, select the repository and set main file path to `app.py`.
3. Deploy. `requirements.txt` is included.
4. The app uses Open-Meteo for weather. If the endpoint is unavailable, the app clearly shows weather as unavailable and continues with local inputs.

For production, use a managed database, authentication, HTTPS, monitoring, privacy notice and reviewed local agronomy content. Streamlit Community Cloud's local filesystem may be ephemeral; do not rely on SQLite history for permanent production storage.

## Agent workflow
`FarmSupervisor.run()` orchestrates independent deterministic agents in `agents.py`. Each agent returns structured findings. The supervisor applies transparent conditions to build a prioritized plan. This is an auditable agentic workflow prototype, not a fully autonomous system and not an LLM making unverified agricultural decisions.

## Data and APIs
- Weather: Open-Meteo forecast API, no API key required. See https://open-meteo.com/ for terms and attribution requirements.
- Local guidance: `data/agri_knowledge.json` is a small illustrative knowledge base. Replace/extend it with reviewed, region-specific sources and preserve source title, issuing body, publication date and URL for each entry before deployment.
- Farm assessments: SQLite database `agripilot.db` is created locally.

## Suggested validation before real-world pilot
1. Test with farmers and agriculture officers in the target district.
2. Compare irrigation suggestions against field moisture readings and local crop calendars.
3. Validate every knowledge-base entry with KVK / state agriculture department material.
4. Evaluate symptom triage against expert-labelled field cases; report precision/recall and abstention rate.
5. Add consent, data retention controls and access permissions before collecting identifiable farmer information.
