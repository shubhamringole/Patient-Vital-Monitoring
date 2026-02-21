
# Real-Time Patient Vitals Monitoring Pipeline (GCP)
## 📌 Project Overview
This project implements a real-time end-to-end streaming data pipeline on Google Cloud Platform (GCP) to simulate and process patient vital signs data.
The pipeline:

- Simulates patient vitals (heart rate, SpO2, temperature, blood pressure)
- Streams data to Pub/Sub
- Processes data using Apache Beam on Dataflow
- Implements Medallion Architecture (Bronze → Silver → Gold)
- Stores final results in BigQuery
- Visualizes risk metrics in Power BI (DirectQuery)
  
# Architecture Diagram

<img width="764" height="310" alt="PatientVitalMonitoring drawio" src="https://github.com/user-attachments/assets/36b1cac5-81e3-4253-bb57-339b511c60ba" />

## 🛠 Tech Stack
1. Google Cloud Pub/Sub
2. Google Cloud Dataflow
3. Apache Beam (Python SDK)
4. Google Cloud Storage (GCS)
5. BigQuery
6. Power BI (DirectQuery Mode)
7. Python
8. dotenv

## 📂 Project Structure
```
<
patient-vital-monitoring/
│
├── simulator/
│   └── patient_vitals_simulator.py
│
├── dataflow/
│   └── streaming_medallion_pipeline.py
│
├── .env (configuration)
└── README.md
/>
```
## 1️⃣ Patient Vitals Simulator (Publisher)
This script generates synthetic patient vitals data and publishes messages to a Pub/Sub topic.

### Features

- Random patient ID generation
- Realistic vital ranges
- Error injection (10% default)
- Synchronous publish confirmation (future.result())

  
## Example Record
```
{
  "patient_id": "P012",
  "timestamp": "2026-02-21T10:15:30Z",
  "heart_rate": 95.2,
  "spo2": 97.1,
  "temperature": 37.2,
  "bp_systolic": 120.3,
  "bp_diastolic": 78.4
}
```
## Error Injection Types

- Missing field
- Negative heart rate
- Out-of-range SpO2


# 2️⃣ Streaming Dataflow Pipeline (Apache Beam)
The pipeline runs in streaming mode and processes data through 3 layers.


### 🥉 Bronze Layer (Raw Data)

- Reads from Pub/Sub subscription
- Decodes messages
- Windows data into 60-second intervals
- Writes raw JSON to GCS

### Storage Path:
```
gs://patients-vitals-streaming-shu/bronze/
```
### 🥈 Silver Layer (Cleaned + Enriched)

#### Validation Rules

- No null fields
- SpO2 between 0–100
- Heart rate between 60–120
- Temperature between 36–39
- Blood pressure within valid range

# Enrichment Logic
Risk score formula:
```
risk_score =
(heart_rate / 200) * 0.4 +
(temperature / 40) * 0.3 +
(1 - spo2 / 100) * 0.3
```
## Risk Levels:

- < 0.3 → Low
- 0.3 – 0.6 → Medium
- 0.6 → High

### Storage Path:
```
gs://patients-vitals-streaming-shu/silver/
```
# 🥇 Gold Layer (Aggregated Analytics)

- Groups records by patient_id
- Calculates averages:

- avg_heart_rate
  * avg_spo2
  * avg_temperature
  * avg_bp_systolic
  * avg_bp_diastolic

- Determines highest risk level
- Writes results to BigQuery

## BigQuery Table:
```
project-ecc895b4-2063-4e3f-b25.healthcare.patient_risk_analytics
```
# ⚙️ Configuration (.env)
Simulator Config
```
GCP_PROJECT=project-ecc895b4-2063-4e3f-b25
PUBSUB_TOPIC=patient_vitals_stream
PATIENT_COUNT=20
STREAM_INTERVAL=2
ERROR_RATE=0.1
```
Dataflow Config
```
GCP_PROJECT=project-ecc895b4-2063-4e3f-b25
PUBSUB_SUBSCRIPTION=projects/project-ecc895b4-2063-4e3f-b25/subscriptions/patient_vitals_subscription
BRONZE_PATH=gs://patients-vitals-streaming-shu/bronze/
SILVER_PATH=gs://patients-vitals-streaming-shu/silver/
BIGQUERY_TABLE=project-ecc895b4-2063-4e3f-b25.healthcare.patient_risk_analytics
TEMP_LOCATION=gs://patients-vitals-streaming-shu/temp/
STAGING_LOCATION=gs://patients-vitals-streaming-shu/staging/
REGION=us-central1
```

# ▶️ How to Run
Step 1 – Install Dependencies
```
pip install google-cloud-pubsub apache-beam[gcp] python-dotenv
```
Step 2 – Start Simulator
```
python patient_vitals_simulator.py
```
Step 3 – Run Dataflow Pipeline
```
python streaming_medallion_pipeline.py \
  --runner DataflowRunner \
  --region us-east1 \
  --worker_machine_type=e2-small \
  --num_workers=1 \
  --max_num_workers=1 \
  --streaming
```

Step 4 – Verify
- Check Pub/Sub backlog
- Verify GCS bronze/silver folders
- Query BigQuery table
- Connect Power BI using DirectQuery

# 🧾 Git Setup & Version Control

# 1️⃣ Initialize Git Repository (First Time Only)
### If this is a new project:
```
git init
git branch -M main
```
# 2️⃣ Create .gitignore (IMPORTANT)
Create a .gitignore file to avoid pushing secrets and temp files.
```
touch .gitignore
```
Add this inside .gitignore:

```
# Python
__pycache__/
*.pyc

# Virtual environment
venv/

# Environment variables
.env

# Dataflow temp files
*.log
```
⚠️ Never push .env to GitHub.

# 3️⃣ Add Files to Git
Add all project files:
```
git add .
```
# 4️⃣ Commit Changes
```
git commit -m "Initial commit - Real-time patient vitals streaming pipeline"
```
# 5️⃣ Connect to GitHub Repository
After creating a repo on GitHub, copy the HTTPS URL and run:

```
git remote add origin https://github.com/yourusername/patient-vital-monitoring.git
```
Verify:
```
git remote -v
```
# 6️⃣ Push to GitHub
```
git push -u origin main
```
If asked for credentials:
- Use your GitHub username
- Use a Personal Access Token (PAT) as password



git init
git remote add origin https://github.com/shubhamringole/Patient-Vital-Monitoring.git
git add .
git commit -m "Initial commit - streaming medallion pipeline"
git branch -M main
git push -u origin main
