import json
import logging
import os
import sys

from package.database import Database
from utils import BlackBoardUtils, MifitUtils, Utils
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule, IngestModule
from org.sleuthkit.datamodel import BlackboardArtifact, BlackboardAttribute



class MifitIngestModule(DataSourceIngestModule):
    def __init__(self, settings):
        # Set logging path to autopsy log
        Utils.setup_custom_logger(os.path.join(
            Case.getCurrentCase().getLogDirectoryPath(), "autopsy.log.0"))
        self.artifacts = {
            'heartRate': BlackBoardUtils.create_artifact_type("MIFIT", "MIFIT_HR", "Heart Rate Records"),
            'alarm': BlackBoardUtils.create_artifact_type("MIFIT", "MIFIT_ALARM", "Alarms"),
            'steps': BlackBoardUtils.create_artifact_type("MIFIT", "MIFIT_STEPS", "Steps"),
            'sleep': BlackBoardUtils.create_artifact_type("MIFIT", "MIFIT_SLEEP", "Sleep"),
            'workout': BlackBoardUtils.create_artifact_type("MIFIT", "MIFIT_WORKOUT", "Workouts"),
            'userInfo': BlackBoardUtils.create_artifact_type("MIFIT", "MIFIT_USER", "User Info"),
            'stress': BlackBoardUtils.create_artifact_type("MIFIT", "MIFIT_STRESS", "Stress"),
        }

        self.attributes = {
            'heartRate': BlackBoardUtils.create_attribute_type('MIFIT_HR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Heart Rate"),
            'enabled': BlackBoardUtils.create_attribute_type('MIFIT_ENABLED', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Enabled"),
            'start': BlackBoardUtils.create_attribute_type('MIFIT_START', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Start"),
            'stop': BlackBoardUtils.create_attribute_type('MIFIT_STOP', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Stop"),
            'mode': BlackBoardUtils.create_attribute_type('MIFIT_MODE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Mode"),
            'distance': BlackBoardUtils.create_attribute_type('MIFIT_DISTANCE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Distance"),
            'calories': BlackBoardUtils.create_attribute_type('MIFIT_CALORIES', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Calories"),
            'steps': BlackBoardUtils.create_attribute_type('MIFIT_STEPS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Steps"),
            'type': BlackBoardUtils.create_attribute_type('MIFIT_TYPE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Type"),
            'datestr': BlackBoardUtils.create_attribute_type('MIFIT_DATESTR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Date"),
            'cadence': BlackBoardUtils.create_attribute_type('MIFIT_CADENCE', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Cadence"),
            'startTime': BlackBoardUtils.create_attribute_type('MIFIT_STARTTIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Start TIme"),
            'endTime': BlackBoardUtils.create_attribute_type('MIFIT_ENDTIME', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "End Time"),
            'from': BlackBoardUtils.create_attribute_type('MIFIT_FROM', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "From"),
            'to': BlackBoardUtils.create_attribute_type('MIFIT_TO', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "To"),

            'provider': BlackBoardUtils.create_attribute_type('MIFIT_PROVIDER', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Provider"),
            'registDate': BlackBoardUtils.create_attribute_type('MIFIT_REGIST', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DATETIME, "Regist Date"),
            'appToken': BlackBoardUtils.create_attribute_type('MIFIT_APPTOKEN', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "App Token"),
            'loginToken': BlackBoardUtils.create_attribute_type('MIFIT_LOGINTOKEN', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Login Token"),
            'idToken': BlackBoardUtils.create_attribute_type('MIFIT_IDTOKEN', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Token Id"),
            'thirdId': BlackBoardUtils.create_attribute_type('MIFIT_THIRDID', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Third Party Id"),
            'stress': BlackBoardUtils.create_attribute_type('MIFIT_STRESS', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Stress Value"),
        }

        # Context of the ingest
        self.context = None

        # Module Settings choosed in ingest settings
        self.settings = settings

        # Filemanager for this case
        self.fileManager = Case.getCurrentCase().getServices().getFileManager()

    def startUp(self, context):
        # Set the environment context
        self.context = context

    def process(self, dataSource, progressBar):
        # Set progressbar to an scale of 100%
        self.progressBar = progressBar
        progressBar.switchToDeterminate(100)

        # Files
        self.db_origin = self.fileManager.findFiles(dataSource, "%origin_db_%")
        self.db_stress = self.fileManager.findFiles(dataSource, "%stress__%.db")
        self.xml_sdk = self.fileManager.findFiles(dataSource, "hm_id_sdk_android.xml")
        


        for file in self.db_origin:
            with open(file.getLocalPath(), 'rb') as f:
                self.analyze_origin(file)
                f.close()

        for file in self.xml_sdk:
            with open(file.getLocalPath(), 'rb') as f:
                self.analyze_sdk(file)
                f.close()

        for file in self.db_stress:
            with open(file.getLocalPath(), 'rb') as f:
                self.analyze_stress(file)
                f.close()

        # Handle analysis

    def analyze_origin(self, file):
        # self.art_heartRate = BlackBoardUtils.create_artifact_type("MIFIT", "MIFIT_HR", "Heart Rate")
        # self.att_hr = BlackBoardUtils.create_attribute_type('MIFIT_HR', BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Heart Rate")

        try:
            database = Database(file.getLocalPath())
# Heart Rate
            results = database.execute_query(
                "select TIME, HR, DEVICE_ID from HEART_RATE")
            for entry in results:
                try:
                    artifact = file.newArtifact(
                        self.artifacts.get('heartRate').getTypeID())

                    attributes = []
                    attributes.append(BlackboardAttribute(
                        BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, file.getLocalPath(), entry[0]))
                    attributes.append(BlackboardAttribute(self.attributes.get(
                        'heartRate'), file.getLocalPath(), str(entry[1])))
                    attributes.append(BlackboardAttribute(
                        BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DEVICE_ID, file.getLocalPath(), str(entry[2])))
                    artifact.addAttributes(attributes)
                    BlackBoardUtils.index_artifact(
                        artifact, self.artifacts.get('heartRate'))                
                except:
                    pass

# Alarms
            logging.info("Parsing Alarm Data")

            results = database.execute_query(
                "select CALENDAR, ENABLED from ALARM")

            for entry in results:
                try:
                    artifact = file.newArtifact(
                    self.artifacts.get('alarm').getTypeID())

                    attributes = []
                    attributes.append(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, file.getLocalPath(), int(entry[0])/1000))
                    attributes.append(BlackboardAttribute(self.attributes.get('enabled'), file.getLocalPath(), str(entry[1])))
                    artifact.addAttributes(attributes)
                    BlackBoardUtils.index_artifact(artifact, self.artifacts.get('alarm'))
                except:
                    pass


# Summary data
            logging.info("Parsing Activities Data")
            results = database.execute_query(
                "select SOURCE, DATE, SUMMARY, DATA from DATE_DATA")

            for entry in results:
                try:
                    summary = json.loads(entry[2])
                    
                    # steps data
                    if summary.get("stp") and summary.get("stp").get("stage"):
                        for step_record in summary.get("stp").get("stage"):
                            artifact = file.newArtifact(
                                self.artifacts.get('steps').getTypeID())
                            attributes = []
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'datestr'), file.getLocalPath(), str(entry[1])))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'from'), file.getLocalPath(), Utils.minutes_to_time(step_record.get("start"))))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'to'), file.getLocalPath(), Utils.minutes_to_time(step_record.get("stop"))))
                            attributes.append(BlackboardAttribute(self.attributes.get('mode'), file.getLocalPath(
                            ), MifitUtils.mode_to_activity(str(step_record.get("mode")))))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'distance'), file.getLocalPath(), str(step_record.get("dis"))))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'calories'), file.getLocalPath(), str(step_record.get("cal"))))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'steps'), file.getLocalPath(), str(step_record.get("step"))))
                            artifact.addAttributes(attributes)
                            BlackBoardUtils.index_artifact(
                                artifact, self.artifacts.get('steps'))
                except:
                    pass
                # sleep data

                if summary.get("slp") and summary.get("slp").get("stage"):

                    try:
                        for sleep_record in summary.get("slp").get("stage"):
                            artifact = file.newArtifact(
                                self.artifacts.get('sleep').getTypeID())

                            attributes = []
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'datestr'), file.getLocalPath(), str(entry[1])))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'from'), file.getLocalPath(), Utils.minutes_to_time(sleep_record.get("start"))))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'to'), file.getLocalPath(), Utils.minutes_to_time(sleep_record.get("stop"))))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'mode'), file.getLocalPath(), MifitUtils.mode_to_sleep(str(sleep_record.get("mode")))))

                            artifact.addAttributes(attributes), BlackBoardUtils.index_artifact(artifact, self.artifacts.get('sleep'))
                    except:
                        pass
                # Workouts

            results = database.execute_query(
                "select TYPE, DATE, TRACKID, DISTANCE, COSTTIME, CAL, PACE, SFREQ, AVGHR, TOTAL_STEP, ENDTIME from TRACKRECORD")

            for entry in results:

                try:
                    artifact = file.newArtifact(
                        self.artifacts.get('workout').getTypeID())
                    attributes = []
                    attributes.append(BlackboardAttribute(self.attributes.get(
                        'type'), file.getLocalPath(), str(entry[0])))
                    attributes.append(BlackboardAttribute(self.attributes.get(
                        'startTime'), file.getLocalPath(), int(entry[2])))
                    attributes.append(BlackboardAttribute(self.attributes.get(
                        'endTime'), file.getLocalPath(), int(entry[10])))
                    attributes.append(BlackboardAttribute(self.attributes.get(
                        'distance'), file.getLocalPath(), str(entry[3])))
                    attributes.append(BlackboardAttribute(self.attributes.get(
                        'calories'), file.getLocalPath(), str(entry[5])))
                    attributes.append(BlackboardAttribute(self.attributes.get(
                        'steps'), file.getLocalPath(), str(entry[9])))
                    artifact.addAttributes(attributes)
                    BlackBoardUtils.index_artifact(
                        artifact, self.artifacts.get('workout'))
                except:
                    pass

        except Exception as e:
            logging.warning("Error parsing Origin Database: " + str(e))


    def analyze_stress(self, file):
        
        logging.info("Parsing Stress Data")
        
        try:
            database = Database(file.getLocalPath())
    # stress
            results = database.execute_query(
                "select data from AllDayStress;")

            for entry in results:
                try:
                    records = json.loads(entry[0])
                    
                    # steps data
                    if records:
                        for stress_record in records:
                            artifact = file.newArtifact(
                                self.artifacts.get('stress').getTypeID())
                            attributes = []
                            attributes.append(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, file.getLocalPath(), int(stress_record.get("time"))/1000))
                            attributes.append(BlackboardAttribute(self.attributes.get(
                                'stress'), file.getLocalPath(), str(stress_record.get("value"))))
                            artifact.addAttributes(attributes)
                            BlackBoardUtils.index_artifact(
                                artifact, self.artifacts.get('stress'))
                except:
                    pass

        except Exception as e:
            logging.warning("Error parsing Stress Database: " + str(e))


    def analyze_sdk(self, file):
        
        logging.info("Parsing User Info from SDK File")
        
        try:
            xml_file = file.getLocalPath()

            values = Utils.xml_attribute_finder(xml_file)

            for key, value in values.items():
                try:
                    if key == "ti":
                        dump = json.loads(value.encode('utf-8'))
                        logging.warning(dump)

                        artifact = file.newArtifact(self.artifacts.get('userInfo').getTypeID())
                        attributes = []

                        attributes.append(BlackboardAttribute(self.attributes.get('provider'), file.getLocalPath(), str(dump.get("provider"))))
                        attributes.append(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_COUNTRY, file.getLocalPath(), str(dump.get("regist_info").get("country_code").encode('utf-8'))))
                        attributes.append(BlackboardAttribute(self.attributes.get('registDate'), file.getLocalPath(), int(dump.get("regist_info").get("regist_date"))/1000))
                        attributes.append(BlackboardAttribute(self.attributes.get('appToken'), file.getLocalPath(), str(dump.get("token_info").get("app_token").encode('utf-8'))))
                        attributes.append(BlackboardAttribute(self.attributes.get('loginToken'), file.getLocalPath(), str(dump.get("token_info").get("login_token").encode('utf-8'))))
                        attributes.append(BlackboardAttribute(self.attributes.get('idToken'), file.getLocalPath(), str(dump.get("token_info").get("user_id").encode('utf-8'))))
                        attributes.append(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL, file.getLocalPath(), str(dump.get("thirdparty_info").get("email").encode('utf-8'))))
                        attributes.append(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_NAME_PERSON, file.getLocalPath(), str(dump.get("thirdparty_info").get("nickname").encode('utf-8'))))
                        attributes.append(BlackboardAttribute(self.attributes.get('thirdId'), file.getLocalPath(), str(dump.get("thirdparty_info").get("third_id").encode('utf-8'))))
                        
                        artifact.addAttributes(attributes)
                        
                        BlackBoardUtils.index_artifact(artifact, self.artifacts.get('userInfo'))
                
                except Exception as e:
                    logging.warning("Error parsing SDK shared preferences XML File: " + str(e))
        
        except Exception as e:
            logging.warning("Error parsing SDK shared preferences XML File: " + str(e))


class ProgressJob:
    def __init__(self, progressBar, jobs, maxValue=100):
        if jobs < 1:
            jobs = 1
        if maxValue < 1:
            maxValue = 1

        self.maxValue = maxValue
        self.atualPercent = 0
        self.increment = int(100 / (jobs + 1))
        self.progressBar = progressBar

    def next_job(self, message):
        self.atualPercent += self.increment

        if self.atualPercent > self.maxValue:
            self.atualPercent = self.maxValue

        self.progressBar.progress(message, self.atualPercent)

    def change_text(self, message):
        self.progressBar.progress(message)
