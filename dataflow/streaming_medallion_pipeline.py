import os
import json
from dotenv import load_dotenv
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms.window import FixedWindows

#Load Enviroment Vairables
load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT")
PUBSUB_SUBSCRIPTION = os.getenv("PUBSUB_SUBSCRIPTION")
BRONZE_PATH = os.getenv("BRONZE_PATH")
SILVER_PATH = os.getenv("SILVER_PATH")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")
TEMP_LOCATION = os.getenv("TEMP_LOCATION")
STAGING_LOCATION = os.getenv("STAGING_LOCATION")
REGION = os.getenv("REGION")

#Beam Pipeline Options

pipeline_options = PipelineOptions(
    project = PROJECT_ID,
    streaming = True,
    region = REGION,
    staging_location = STAGING_LOCATION,
    temp_location = TEMP_LOCATION
)

#Parse

def parse_json(message):
    try:
        return json.loads(message) #conver json to dictonery
    except:
        return None

def is_valid_record(record):
    try:
        if record is None:
            return False
        p_id = record.get("patient_id")
        hr = record.get("heart_rate")
        spo2 = record.get("spo2")
        temp = record.get("temperature")
        bp_systolic = record.get("bp_systolic")
        bp_diastolic = record.get("bp_diastolic")
        #Validate NOne Fields

        if p_id is None or hr is None or spo2 is None or temp is None or bp_systolic is None or bp_diastolic is None:
            return False
        #Validate Range

        if not(0 <spo2 <= 100):
            return False
        if not(60 <= hr <= 120):
            return False
        if not(36 <= temp <= 39):
            return False
        if not(90 <= bp_systolic <= 140):
            return False
        if not(60 <= bp_diastolic <= 90):
            return False
        return True
    except Exception:
        return False

def enrich_record(record):
    record['risk_score']=(                                  #formula from google online
        (record['heart_rate']/200)*0.4+
        (record['temperature']/40)*0.3+
        (1-record['spo2']/100)*0.3
    )
    if record["risk_score"]< 0.3:
        record["risk_level"]="Low"
    elif record["risk_score"]<0.6:
        record["risk_level"]="Medium"
    else:
        record["risk_level"]="High"
    return record


#Pipeline 
with beam.Pipeline(options=pipeline_options) as p:
    
    #Brone
    bronze_data = (
        p
        | "ReadFromPubSub" >> beam.io.ReadFromPubSub(subscription=PUBSUB_SUBSCRIPTION)
        | "Decode to String" >> beam.Map(lambda x: x.decode("utf-8"))
        | "Window bronze data" >> beam.WindowInto(FixedWindows(60))
    )
    bronze_data | "Write Bronze Data to GCS" >> beam.io.WriteToText(
        BRONZE_PATH + "raw_data",
        file_name_suffix=".json"
    )

    #Silver Layer 
    silver_data = (
        bronze_data
        | "Parse JSON" >> beam.Map(parse_json)
        | "Filter Valid Records" >> beam.Filter(is_valid_record)
        | "Enrich Record" >> beam.Map(enrich_record)
        | "Window silver data" >> beam.WindowInto(FixedWindows(60))
    )
    silver_data | "Write Silver Data to GCS" >> beam.io.WriteToText(
        SILVER_PATH + "Clean_data", file_name_suffix=".json")
    
    #Gold Layer

    def extract_for_aggregation(record):
        return (record["patient_id"], record)

    def aggregated_records(key_values):
        patient_id,records = key_values
        count = len(records)
        avg_heart_rate = sum(record["heart_rate"] for record in records) / count
        avg_spo2 = sum(record["spo2"] for record in records) / count
        avg_temperature = sum(record["temperature"] for record in records) / count
        avg_bp_systolic = sum(record["bp_systolic"] for record in records) / count
        avg_bp_diastolic = sum(record["bp_diastolic"] for record in records) / count
        risk_levels = [record["risk_level"] for record in records]
        if "High" in risk_levels:
            risk_level = "High"
        elif "Medium" in risk_levels:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        return {
            "patient_id": patient_id,
            "count": count,
            "avg_heart_rate": avg_heart_rate,
            "avg_spo2": avg_spo2,
            "avg_temperature": avg_temperature,
            "avg_bp_systolic": avg_bp_systolic,
            "avg_bp_diastolic": avg_bp_diastolic,
            "risk_level": risk_level
        }
    
    gold_data = (
        silver_data
        | "Key by patient ID" >> beam.Map(extract_for_aggregation)
        | "Group by Patient ID" >> beam.GroupByKey()
        | "Aggregate per patient" >> beam.Map(aggregated_records)
    )

    #write to gold layer Big Query
    gold_data | "Write to BigQuery" >> beam.io.WriteToBigQuery(
        BIGQUERY_TABLE,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
    ) 





