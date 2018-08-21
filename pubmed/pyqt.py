import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLineEdit, QMessageBox, 
	QLabel, QTextEdit, QGridLayout, QRadioButton, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

import api
from goldencorpus import GoldenCorpus
from mesh_explosion import DataForEachMeshTerm
from clusterer import Clusterer
from postprocessing import PostProcessing

 
class App(QWidget):

	def __init__(self):
		super().__init__()
		self.title = 'PyQt5'
		self.left = 10
		self.top = 10
		self.width = 640
		self.height = 480
		self.fileselected = 0
		self.fileName = ""
		self.rel_docs = []
		self.mesh_terms = []
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		# Create grid
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.grid.setSpacing(0)	
		
		# Search field
		self.searchbox = QLineEdit(self)
		self.searchbox.move(50, 20)
		self.searchbox.resize(280,40)
		
		# Search button
		self.button = QPushButton('Search', self)
		self.button.setToolTip('Search')
		self.button.clicked.connect(self.search_click)

		# Add first row to grid
		self.grid.addWidget(self.searchbox,0,0,1,5)
		self.grid.addWidget(self.button,0,5)

		# gene of docs select
		self.gene_button = QRadioButton("Relevant Genes")
		self.gene_button.setChecked(True)
		self.pmid_button = QRadioButton("Relevant PMID list ")
		self.choose_file = QPushButton('Choose File')
		self.choose_file.clicked.connect(self.chooseFile)
		# self.choose_file.setStyleSheet('border-radius: 1px')
		self.filelabel = QLabel(self)

		# Add second row to grid
		self.grid.addWidget(self.gene_button,1,0,1,2)
		self.grid.addWidget(self.pmid_button,1,1,1,2)
		self.grid.addWidget(self.choose_file,1,3)
		self.grid.addWidget(self.filelabel,1,4)

		# Recommend label and Third row
		self.mtlabel = QLabel('Recommended search Terms: ')
		self.mtlabel.setFixedHeight(40)
		self.dummy = QLabel(' ')
		self.grid.addWidget(self.mtlabel,2,0)
		self.grid.addWidget(self.dummy,2,10)

		# Show best MeshTerms
		self.mt1 = QPushButton('')
		self.mt1.setStyleSheet('border: None; text-decoration: underline')
		self.mt1.clicked.connect(self.representative_click)
		# self.mt2 = QPushButton('')
		# self.mt2.setStyleSheet('border: None; text-decoration: underline')
		# self.mt2.clicked.connect(lambda:self.meshterm_click(self.mt2))
		# self.mt3 = QPushButton('')
		# self.mt3.setStyleSheet('border: None; text-decoration: underline')
		# self.mt3.clicked.connect(lambda:self.meshterm_click(self.mt3))
		# self.mt4 = QPushButton('')
		# self.mt4.setStyleSheet('border: None; text-decoration: underline')
		# self.mt4.clicked.connect(lambda:self.meshterm_click(self.mt4))
		# self.mt5 = QPushButton('')
		# self.mt5.setStyleSheet('border: None; text-decoration: underline')
		# self.mt5.clicked.connect(lambda:self.meshterm_click(self.mt5))

		# Add Fourth row to grid
		self.grid.addWidget(self.mt1,3,0,1,4)
		# self.grid.addWidget(self.mt2,3,1)
		# self.grid.addWidget(self.mt3,3,2)
		# self.grid.addWidget(self.mt2,3,3)
		# self.grid.addWidget(self.mt3,3,4)

		# Top result placeholder buttons
		self.title1 = QPushButton('Title one')
		self.title1.setStyleSheet('border: None; text-decoration: underline; padding-top: 40px')
		self.abs1 = QTextEdit("dksjfahsdkajhvkjsdvnsafnkjsdhfkjsdagksdafkdsagkjshfiurhfirnviunvirueanifudsiuvnsivndfnvaianvirnekngifuanvifnvkfnd")
		self.abs1.setReadOnly(True)
		self.title2 = QPushButton('Title two')
		self.title2.setStyleSheet('border: None; text-decoration: underline')
		self.abs2 = QTextEdit("uyrwejsvniunfksdaffffbdfuanvkjsdnvlksdnfhgfldnfksdnflsndf")
		self.abs2.setReadOnly(True)
		self.title3 = QPushButton('Title three')
		self.title3.setStyleSheet('border: None; text-decoration: underline')
		self.abs3 = QTextEdit("vxc,mnvureglsavnlskdvmldfnbknlmncljsdncvkjdnvlkjdfns")
		self.abs3.setReadOnly(True)

		# Add Fourth row to grid
		self.grid.addWidget(self.title1,4,0,1,5)
		self.grid.addWidget(self.abs1,5,0,2,5)
		self.grid.addWidget(self.title2,7,0,1,5)
		self.grid.addWidget(self.abs2,8,0,2,5)
		self.grid.addWidget(self.title3,11,0,1,5)
		self.grid.addWidget(self.abs3,12,0,2,5)

		# Visualization
		self.vizlabel = QLabel("Visualization: ")
		self.vizlabel.setStyleSheet('padding-top: 40px')
		self.genecloud = QPushButton('Genes cloud')
		self.genecloud.setStyleSheet('border: None; text-decoration: underline')
		self.meshcloud = QPushButton('Mesh cloud')
		self.meshcloud.setStyleSheet('border: None; text-decoration: underline')
		self.grid.addWidget(self.vizlabel,4,7)
		self.grid.addWidget(self.genecloud,5,7)
		self.grid.addWidget(self.meshcloud,6,7)

		self.show()

	@pyqtSlot()
	def search_click(self):
		_textval = self.searchbox.text()
		self._search_term = _textval
		if self.gene_button.isChecked() and self.fileselected:
			if self.fileName:
				goldencorpus = GoldenCorpus(_textval,self.fileName)
				goldencorpus.fetchData()
				self.rel_docs = goldencorpus.get_rel_docs_pmid()
				self.mesh_terms = goldencorpus.get_mesh_terms()
				mesh_explosion = DataForEachMeshTerm(self.mesh_terms,_textval)
				path = mesh_explosion.get_data_foldername(_textval)
				print("sending rel_docs: ",len(self.rel_docs))
				clus = Clusterer(self.rel_docs,path,True,8)
				self.representative_id,representative,best_mesh_terms_id, best_mesh_terms = clus.cluster()
				self.mt1.setText(representative)
				# self.populateTitleAbs(json_no)
			else:
				print("Error! getting file name")
		elif self.pmid_button.isChecked():
			print("Golden corpus exists..")
		else:
			print("Please select related file..")
	def representative_click(self):
		text = self.mt1.text()
		self.searchbox.setText(text)
		self.populateTitleAbs(self.representative_id)

	def populateTitleAbs(self,json_no):
		index = 0
		pp = PostProcessing()
		titles , abstracts = pp.getTitleAbs(index,json_no,self._search_term)
		print(titles)

	def chooseFile(self): 
		if self.fileselected:
			self.filelabel.setText("")
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		self.fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
		if self.fileName:
			self.filelabel.setText(self.fileName)
			self.fileselected = 1;
	


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())
