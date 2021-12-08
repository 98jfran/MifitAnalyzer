import os
import sys
import logging

from org.sleuthkit.autopsy.ingest import GenericIngestModuleJobSettings
from org.sleuthkit.autopsy.report import GeneralReportModuleAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.corecomponentinterfaces import DataSourceProcessor  
from org.sleuthkit.autopsy.casemodule import Case

from ingest import MifitIngestModule
from settings import MifitIngestSettingsPanel

from utils import Utils, SettingsUtils, MifitUtils, BlackBoardUtils

class MifitIngestModuleFactory(IngestModuleFactoryAdapter):
    moduleName = "Mifit Android App Analyzer"

    def __init__(self):
        self.settings = None
        
    #Module Settings
    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Mifit Analyzer for Autopsy"
        
    def getModuleVersionNumber(self):
        return "1.0"
    
    #Data Source Ingest
    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return MifitIngestModule(self.settings)

    #Settings
    def getDefaultIngestJobSettings(self):
        return GenericIngestModuleJobSettings()
    
    def hasIngestJobSettingsPanel(self):
        return True

    def getIngestJobSettingsPanel(self, settings):
        if not isinstance(settings, GenericIngestModuleJobSettings):
            raise IllegalArgumentException("Expected settings argument to be instanceof GenericIngestModuleJobSettings")
        
        self.settings = settings
        return MifitIngestSettingsPanel(self.settings)



