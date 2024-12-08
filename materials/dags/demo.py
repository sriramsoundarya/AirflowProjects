import json
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import psycopg2
import os

# Default arguments
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
    'depends_on_past':False
}
# Path to the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the DAG
with DAG(
    'json_to_postgres_dag',
    default_args=default_args,
    schedule_interval=None,  # Run on demand
    catchup=False
) as dag:
    startBash=BashOperator(task_id='Bashin',bash_command='echo started process')
    # Step 1: Parse JSON and prepare records
    def parse_json_to_record():
        # Path to the JSON file
        json_path = os.path.join(script_dir, "employee.json")
        print(json_path)
        # Load JSON data
        with open(json_path, 'r') as file:
            data = json.load(file)

        # Prepare records
        employee_records = []
        skills_records = []
        projects_records = []

        for employee in data["employees"]:
            # Employees table
            employee_records.append((
                employee["id"],
                employee["name"]["first"],
                employee["name"]["last"],
                employee["contact"]["email"],
                employee["contact"]["phone"],
                employee["address"]["city"],
                employee["address"]["state"],
                employee["address"]["zip"]
            ))

            # Skills table
            for skill in employee["skills"]:
                skills_records.append((
                    employee["id"],  # Link skill to employee
                    skill["name"],
                    skill["experience"]
                ))

            # Projects table
            for project in employee["projects"]:
                projects_records.append((
                    employee["id"],  # Link project to employee
                    project["project_id"],
                    project["project_name"],
                    project["duration"]
                ))

        # Save records to XCom
        return {
            'employee_records': employee_records,
            'skills_records': skills_records,
            'projects_records': projects_records,
        }

    parse_json_task = PythonOperator(
        task_id='parse_json_task',
        python_callable=parse_json_to_record,
    )
    startBash>>parse_json_task