import sys
import json
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication,QWidget, QTextEdit, QGridLayout, QLabel,QPushButton)
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt


class TaggingAbstract(QWidget):
    def __init__(self,abstract):
        QWidget.__init__(self)
        self.setWindowTitle("Tagging Entities")
        self.showMaximized()
        # global variables
        self.newgenes = []
        self.noofnewgene = 0

        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)	
        self.layout = QGridLayout()

        self.abs1 = QTextEdit(abstract)
        self.abs1.setStyleSheet('text-align: left; border: None; color: #545454')
        # self.abs1.setReadOnly(True)
        self.newgenelabel = QLabel("")
        self.label = QLabel("See new Gene ?")
        self.addbutton = QPushButton('Send selected Gene', self)
        self.addbutton.setStyleSheet('padding: 7px')
        self.addbutton.setCursor(Qt.PointingHandCursor)
        self.addbutton.setToolTip('Help us with new Gene')
        self.addbutton.clicked.connect(self.get_selected_text)

        self.layout.addWidget(self.abs1,0,0,1,2)
        self.layout.addWidget(self.label,1,0,1,1)
        self.layout.addWidget(self.addbutton,1,1,1,1)
        self.layout.addWidget(self.newgenelabel,2,0,1,1)

        self.setLayout(self.layout)
        self.tag_entities()

    
    def tag_entities(self):
        # read dictionary file here
        hugo = open("Hugo.json",'r')
        dictionary = json.load(hugo)
        docs = dictionary["docs"]
        if len(docs): 
            format = QtGui.QTextCharFormat()
            format.setBackground(QtGui.QBrush(QtGui.QColor("yellow")))
            strval = self.abs1.toPlainText()
            for entry in docs:
                synonyms = []
                synonyms.append(entry["name"])
                synonyms.append(entry["symbol"])
                if "alias_symbol" in entry:
                    for alias in entry["alias_symbol"]:
                        synonyms.append(alias)
                # if "prev_name" in entry:
                #     for prev in entry["prev_name"]:
                #         synonyms.append(prev)
                if "prev_symbol" in entry:
                    for sym in entry["prev_symbol"]:
                        synonyms.append(sym)

                for word in synonyms:
                    cursor = self.abs1.textCursor()
                    index = strval.find(word,0,len(strval))
                    while (index != -1):
                        # Select the matched text and apply the desired format
                        cursor.setPosition(index)
                        cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
                        cursor.mergeCharFormat(format)
                        # Move to the next match
                        pos = index + len(word)
                        index = strval.find(word,pos,len(strval))

    def get_selected_text(self):
        cursor = self.abs1.textCursor()
        textSelected = cursor.selectedText()
        if textSelected:
            self.noofnewgene = self.noofnewgene + 1
            self.newgenes.append(textSelected)
            self.show_new_genes(textSelected)
    def show_new_genes(self,gene):
        if(len(gene)):
            self.newgenelabel.setText("Gene added by you: ")
            self.genelabel = QLabel(gene)
            self.layout.addWidget(self.genelabel)
            