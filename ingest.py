import json
import logging
import os
import sys

from package.database import Database
from gps import Kml
from standalone import Standalone
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
    
    def get_info(self, attr=""):
        try:
            return self.report.get("report").get(attr)
        except Exception as e:
            logging.warning(str(e))

    def startUp(self, context):
        # Set the environment context
        self.context = context

    def process(self, dataSource, progressBar):
        # Set progressbar to an scale of 100%
        self.progressBar = progressBar
        progressBar.switchToDeterminate(100)

        self.start_date = self.settings.getSetting('startDate')
        self.end_date = self.settings.getSetting('endDate')
        self.options = json.loads(self.settings.getSetting('options'))
        self.is_gps = "Index GPS Coordinates" in self.options

        logging.info("Start Date {}".format(self.settings.getSetting('startDate')))
        logging.info("End Date {}".format(self.settings.getSetting('endDate')))
        logging.info("Options {}".format(self.settings.getSetting('options')))

        self.temp_module_path = os.path.join(Case.getCurrentCase().getModulesOutputDirAbsPath(), "Mifit")
        Utils.check_and_generate_folder(self.temp_module_path)

        file = self.fileManager.findFiles(dataSource, "%origin%")[0]
        standalone = Standalone(os.path.dirname(os.path.dirname(file.getLocalPath())), "report.json", self.start_date, self.end_date, True)

        self.report = standalone.analyse()
        file_handler = open(os.path.join(self.temp_module_path, "report.json"), "w")
        file_handler.write(json.dumps(self.report))
        file_handler.close()



        for entry in self.get_info("origin").get("hr"):
            try:
                artifact = file.newArtifact(self.artifacts.get('heartRate').getTypeID())
                attributes = [
                    BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, file.getLocalPath(), entry.get("time")/1000),
                    BlackboardAttribute(self.attributes.get('heartRate'), file.getLocalPath(), entry.get("value")),
                    BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DEVICE_ID, file.getLocalPath(), entry.get("device"))
                ]
                BlackBoardUtils.index_artifact(artifact, self.artifacts.get('heartRate'), attributes)
            except Exception as e:
                logging.warning(str(e))
        
        for entry in self.get_info("origin").get("sleep"):
            try:
                artifact = file.newArtifact(self.artifacts.get('sleep').getTypeID())
                attributes = [
                    BlackboardAttribute(self.attributes.get('datestr'), file.getLocalPath(), entry.get("date")),
                    BlackboardAttribute(self.attributes.get('from'), file.getLocalPath(), entry.get("from")),
                    BlackboardAttribute(self.attributes.get('to'), file.getLocalPath(), entry.get("to")),
                    BlackboardAttribute(self.attributes.get('mode'), file.getLocalPath(), entry.get("mode"))
                    ]
                
                BlackBoardUtils.index_artifact(artifact, self.artifacts.get('sleep'), attributes)
            except:
                    pass

        for entry in self.get_info("origin").get("alarm"):
            try:
                artifact = file.newArtifact(self.artifacts.get('alarm').getTypeID())
                attributes = [
                    BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, file.getLocalPath(), entry.get("time")/1000),
                    BlackboardAttribute(self.attributes.get('enabled'), file.getLocalPath(), entry.get("enabled"))
                ]
                BlackBoardUtils.index_artifact(artifact, self.artifacts.get('alarm'), attributes)
            except:
                pass
        
        for entry in self.get_info("origin").get("steps"):
            try:
                artifact = file.newArtifact(self.artifacts.get('steps').getTypeID())
                attributes = [
                    BlackboardAttribute(self.attributes.get('datestr'), file.getLocalPath(), entry.get("date")),
                    BlackboardAttribute(self.attributes.get('from'), file.getLocalPath(), entry.get("from")),
                    BlackboardAttribute(self.attributes.get('to'), file.getLocalPath(), entry.get("to")),
                    BlackboardAttribute(self.attributes.get('mode'), file.getLocalPath(), entry.get("mode")),
                    BlackboardAttribute(self.attributes.get('distance'), file.getLocalPath(), entry.get("distance")),
                    BlackboardAttribute(self.attributes.get('calories'), file.getLocalPath(), entry.get("calories")),
                    BlackboardAttribute(self.attributes.get('steps'), file.getLocalPath(), entry.get("steps"))
                    ]
                
                BlackBoardUtils.index_artifact(artifact, self.artifacts.get('sleep'), attributes)
            except:
                    pass
        
        for entry in self.get_info("origin").get("workouts"):
            try:
                artifact = file.newArtifact(self.artifacts.get('steps').getTypeID())
                attributes = [
                    BlackboardAttribute(self.attributes.get('mode'), file.getLocalPath(), entry.get("type")),
                    BlackboardAttribute(self.attributes.get('start'), file.getLocalPath(), entry.get("start")),
                    BlackboardAttribute(self.attributes.get('stop'), file.getLocalPath(), entry.get("end")),
                    BlackboardAttribute(self.attributes.get('distance'), file.getLocalPath(), entry.get("distance")),
                    BlackboardAttribute(self.attributes.get('calories'), file.getLocalPath(), entry.get("calories")),
                    BlackboardAttribute(self.attributes.get('steps'), file.getLocalPath(), entry.get("steps"))
                    ]
                
                BlackBoardUtils.index_artifact(artifact, self.artifacts.get('steps'), attributes)
                if self.is_gps:
                    for coordinate in entry.get("coordinates"):
                        try:
                            BlackBoardUtils.add_tracking_point(file, entry.get("start"), coordinate.split(" ")[0], coordinate.split(" ")[1], source=file.getLocalPath())
                        except:
                            pass
            except:
                pass
        
        for entry in self.get_info("stress").get("allDayStress"):
            try:
                artifact = file.newArtifact(self.artifacts.get('stress').getTypeID())
                attributes = [
                    BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_DATETIME, file.getLocalPath(), entry.get("time")/1000),
                    BlackboardAttribute(self.attributes.get('stress'), file.getLocalPath(), entry.get("value")),
                    BlackboardAttribute(self.attributes.get('steps'), file.getLocalPath(), entry.get("steps"))
                ]
                BlackBoardUtils.index_artifact(artifact, self.artifacts.get('stress'), attributes)
            except:
                    pass

        for entry in self.get_info("users").get("userInfo"):
            try:
                artifact = file.newArtifact(self.artifacts.get('userInfo').getTypeID())
                attributes = [
                    BlackboardAttribute(self.attributes.get('provider'), file.getLocalPath(), entry.get("provider")),
                    BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_COUNTRY, file.getLocalPath(), entry.get("provider")),
                    BlackboardAttribute(self.attributes.get('registDate'), file.getLocalPath(), entry.get("registDate")/1000),
                    BlackboardAttribute(self.attributes.get('appToken'), file.getLocalPath(), entry.get("appToken")),
                    BlackboardAttribute(self.attributes.get('loginToken'), file.getLocalPath(), entry.get("loginToken")),
                    BlackboardAttribute(self.attributes.get('idToken'), file.getLocalPath(), entry.get("idToken")),
                    BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_EMAIL, file.getLocalPath(), entry.get("email")),
                    BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_NAME_PERSON, file.getLocalPath(), entry.get("nickname")),
                    BlackboardAttribute(self.attributes.get('thirdId'), file.getLocalPath(), entry.get("thirdId"))
                ]
                BlackBoardUtils.index_artifact(artifact, self.artifacts.get('userInfo'), attributes)
            except:
                    pass

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
