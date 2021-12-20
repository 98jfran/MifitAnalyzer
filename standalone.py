import os
import logging
import json

from package.database import Database
from utils import MifitUtils, Utils

class Standalone:
    def __init__(self, report_path):

        self.report_path = report_path
        pass

    def analyse(self):
        report_struct = {"case":{}, "report":{} }
        report_struct["case"]["number"] = os.environ.get("CASE_NUMBER")
        report_struct["case"]["examinerName"] = os.environ.get("EXAMINER_NAME")
        report_struct["case"]["examinerPhone"] = os.environ.get("EXAMINER_PHONE")
        report_struct["case"]["examinerEmail"] = os.environ.get("EXAMINER_EMAIL")
        report_struct["case"]["examinerNotes"] = os.environ.get("EXAMINER_NOTES")

        origin_dbs = Utils.list_files("C:\\Users\\josef\\Desktop\\a", "origin_db")
        print("test", origin_dbs)

        for db in origin_dbs:
            try:
                    report_struct["report"] = self.analyze_origin(db)
            except:
                pass

        return report_struct
        
        

    def report(self, report, report_path):
        logging.info("Generating report")
        #handle report logic
        return


#MIFIT analyse functions
    def analyze_origin(self, database_path):
        database = Database(database_path)
        hr_records = []

        results = database.execute_query(
            "select TIME, HR, DEVICE_ID from HEART_RATE")
        for entry in results:
            hr_record = {}
            try:
                hr_record["time"] = str(entry[0])
                hr_record["value"] = str(entry[1])
                hr_record["device"] = str(entry[2])
                hr_records.append(hr_record)
            except:
                pass
        results = database.execute_query(
                "select CALENDAR, ENABLED from ALARM")
        
        alarm_records = []
        for entry in results:
            alarm_record = {}
            try:
                alarm_record["time"] = str(entry[0])
                alarm_record["enabled"] = str(entry[1])
                alarm_records.append(alarm_record)
            except:
                pass

        results = database.execute_query(
                "select SOURCE, DATE, SUMMARY, DATA from DATE_DATA")
        
        step_records = []
        for entry in results:
            summary = json.loads(entry[2])
            
            if summary.get("stp") and summary.get("stp").get("stage"):
                summary = json.loads(entry[2])
                for summary_record in summary.get("stp").get("stage"):
                    try:
                        step_record = {}
                        step_record["date"] = str(entry[1])
                        step_record["from"] = Utils.minutes_to_time(summary_record.get("start"))
                        step_record["to"] = Utils.minutes_to_time(summary_record.get("stop"))
                        step_record["mode"] = MifitUtils.mode_to_activity(str(summary_record.get("mode")))
                        step_record["distance"] = str(summary_record.get("dis"))
                        step_record["calories"] = str(summary_record.get("cal"))
                        step_record["steps"] = str(summary_record.get("step"))
                        step_records.append(step_record)
                    except:
                        pass

            # sleep data
            sleep_records = []
            if summary.get("slp") and summary.get("slp").get("stage"):
                for summary_record in summary.get("slp").get("stage"):
                    try:
                        sleep_record = {}
                        sleep_record["date"] = str(entry[1])
                        sleep_record["from"] = Utils.minutes_to_time(summary_record.get("start"))
                        sleep_record["to"] = Utils.minutes_to_time(summary_record.get("stop"))
                        sleep_record["mode"] = MifitUtils.mode_to_sleep(str(summary_record.get("mode")))
                        sleep_records.append(sleep_record)
                    except:
                        pass


        # Workouts
        results = database.execute_query(
                "select TYPE, DATE, TRACKID, DISTANCE, COSTTIME, CAL, PACE, SFREQ, AVGHR, TOTAL_STEP, ENDTIME from TRACKRECORD")
        
        activity_records = []
        
        for entry in results:
            activity_record = {}
            try:
                activity_record["type"] = str(entry[0])
                activity_record["start"] = int(entry[2])
                activity_record["end"] =  int(entry[10])
                activity_record["distance"] = str(entry[3])
                activity_record["calories"] =  str(entry[5])
                activity_record["steps"] = str(entry[9])
                activity_records.append(activity_record)
            except:
                pass

        

        return {"hr": hr_records, "alarm": alarm_records, "sleep": sleep_records, "steps": step_records, "workouts": activity_records}
        

