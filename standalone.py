import os
import logging
import json

from package.database import Database
from utils import MifitUtils, Utils

class Standalone:
    def __init__(self, dump_path="", report_path="report.json"):
        self.dump_path = dump_path
        self.report_path = report_path
        self.report_struct = {}

    def analyse(self):
        self.report_struct = {"case":{}, "report":{}}
        self.report_struct["case"]["number"] = os.environ.get("CASE_NUMBER")
        self.report_struct["case"]["examinerName"] = os.environ.get("EXAMINER_NAME")
        self.report_struct["case"]["examinerPhone"] = os.environ.get("EXAMINER_PHONE")
        self.report_struct["case"]["examinerEmail"] = os.environ.get("EXAMINER_EMAIL")
        self.report_struct["case"]["examinerNotes"] = os.environ.get("EXAMINER_NOTES")

        origin_dbs = Utils.list_files(self.dump_path, "origin_db", ["journal","wal", "-shm"])
        stress_dbs = Utils.list_files(self.dump_path, "stress_", ["journal","wal", "shm"])
        sdk_xmls = Utils.list_files(self.dump_path, "hm_id_sdk_android")

        print(origin_dbs)


        for db in origin_dbs:
            try:
                self.report_struct["report"]["origin"] = self.__analyze_origin(db)
            except Exception as e:
                logging.warning(e)
                pass
                

        for db in stress_dbs:
            try:
                logging.info("Analysing {} database... ".format(db))
                self.report_struct["report"]["stress"] = self.__analyze_stress(db)
            except Exception as e:
                logging.warning(e)
                pass
        
        for xml_file in sdk_xmls:
            try:
                logging.info("Analysing {} file... ".format(xml_file))
                self.report_struct["report"]["users"] = self.__analyze_sdk(xml_file)
            except Exception as e:
                logging.warning(e)
                pass

        return self.report_struct
        
    def report(self):
        logging.info("Generating report...")
        Utils.write_json(self.report_path, self.report_struct)
        js_report = "var reportRAW = " + json.dumps(self.report_struct, indent = 2)
        file_handler = open(os.path.join("./report/js", "report.js"), "w")
        file_handler.write(js_report)
        file_handler.close()
        logging.info("Full HTML report: {}".format(os.path.abspath(os.path.join("./report/index.html"))))
        
    
    @staticmethod
    def detach_report(report, report_path):
        logging.info("Generating detach report...")
        js_report = "var reportRAW = " + json.dumps(report, indent = 2)
        file_handler = open(report_path, "wb")
        file_handler.write(js_report)
        file_handler.close()
        # logging.info("Full HTML report: {}".format(os.path.abspath(os.path.join(os.path.dirname(__file__), "report", "index.html"))))
        return report_path
        



#MIFIT analyse functions
    def __analyze_origin(self, database_path):

        try: 
            database = Database(database_path)
            hr_records = []

            results = database.execute_query(
                "select TIME, HR, DEVICE_ID from HEART_RATE")
            for entry in results:
                hr_record = {}
                try:
                    hr_record["time"] = int(entry[0])
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
                    alarm_record["time"] = int(entry[0])
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
                        except Exception as e:
                            pass
                            logging.warning(e)

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
                        except Exception as e:
                            pass
                            logging.warning(e)


            # Workouts
            results = database.execute_query(
                    "select td.TYPE, tr.DATE, tr.TRACKID, tr.DISTANCE, tr.COSTTIME, tr.CAL, tr.PACE, tr.SFREQ, tr.AVGHR, tr.TOTAL_STEP, tr.ENDTIME, td.BULKLL from TRACKRECORD tr LEFT JOIN TRACKDATA td ON (tr.TRACKID =  td.TRACKID)")
            
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

                    coordinatesRAW = str(entry[11]).split(";")
                    activity_record["coordinates"] = MifitUtils.getCoordinateByBulkArray(coordinatesRAW)
                    activity_records.append(activity_record)
                except Exception as e:
                    logging.warning(e)
        

            return {"hr": hr_records, "alarm": alarm_records, "sleep": sleep_records, "steps": step_records, "workouts": activity_records}
        except:
            pass

    def __analyze_stress(self, database_path):
        
        logging.info("Parsing Stress Data")
        
        stress_records = []

        try:
            database = Database(database_path)
            results = database.execute_query(
                "select data from AllDayStress;")

            for entry in results:
                try:
                    records = json.loads(entry[0])
                    if records:
                        for record in records:
                            stress_record = {}
                            stress_record["time"] = int(record.get("time"))
                            stress_record["value"] = str(record.get("value"))
                            stress_records.append(stress_record)
                except:
                    pass

        except Exception as e:
            pass
            # logging.warning(e)
        
        return {"allDayStress": stress_records}
        

    def __analyze_sdk(self, xml_path):
        values = Utils.xml_attribute_finder(xml_path)
        user_info = {}
        users = []
        for key, value in values.items():
            user_info = {}
            try:
                if key == "ti":
                    dump = json.loads(value)
                    user_info["provider"] = str(dump.get("provider"))
                    user_info["registDate"] = int(dump.get("regist_info").get("regist_date"))
                    user_info["countryCode"] = str(dump.get("regist_info").get("country_code"))
                    user_info["appToken"] = str(dump.get("token_info").get("app_token"))
                    user_info["loginToken"] = str(dump.get("token_info").get("login_token"))
                    user_info["idToken"] = str(dump.get("token_info").get("user_id"))
                    user_info["email"] = str(dump.get("thirdparty_info").get("email"))
                    user_info["nickname"] = str(dump.get("thirdparty_info").get("nickname"))
                    user_info["thirdId"] = str(dump.get("thirdparty_info").get("third_id"))
                    users.append(user_info)
            except Exception as e:
                logging.warning(e)
            
        return {"userInfo": users}