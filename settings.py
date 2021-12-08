import json
import sys
import os

from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from java.awt import Font
from java.awt import Dimension
from java.awt import BorderLayout
from javax.swing import JPanel
from javax.swing import BoxLayout
from javax.swing import ButtonGroup
from javax.swing import JLabel
from collections import OrderedDict

sys.path.append(os.path.dirname(__file__))


from utils import Utils, SettingsUtils, MifitUtils
import logging

class MifitIngestSettingsPanel(IngestModuleIngestJobSettingsPanel):
    def __init__(self, settings):
        self.local_settings = settings
        self.initComponents()

    def initComponents(self):
        self.options_checkboxes_list = []
        self.setLayout(BoxLayout(self, BoxLayout.PAGE_AXIS))
        self.setPreferredSize(Dimension(300,0))
        
        # title 
        self.p_title = SettingsUtils.createPanel()
        self.lb_title = JLabel("Mifit Android App Analyzer")
        self.lb_title.setFont(self.lb_title.getFont().deriveFont(Font.BOLD, 15))
        self.p_title.add(self.lb_title)
        self.add(self.p_title)
        # end of title

        self.p_panel = SettingsUtils.createPanel()
        self.p_panel.add(JLabel("Options available:"))
        

        options =["option1", "option2", "option3", "option4", "option5", "option6"]

        for option in options:
            checkbox = SettingsUtils.createCheckbox(option,self.getSelectedOption, True)
            self.add(checkbox)
            self.options_checkboxes_list.append(checkbox)
            self.p_panel.add(checkbox)

        self.add(self.p_panel)
    
    def getSelectedOption(self, event):
        selected_options = []
        
        for cb_option in self.options_checkboxes_list:
            if cb_option.isSelected():
                selected_options.append(cb_option.getActionCommand())
        
        self.local_settings.setSetting("options", json.dumps(selected_options))

    
    def getSettings(self):
        return self.local_settings

    

