import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLineEdit, QMessageBox, 
	QLabel, QTextEdit, QGridLayout, QRadioButton, QFileDialog, QMainWindow, QDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5 import QtCore

import api
from goldencorpus import GoldenCorpus
from mesh_explosion import DataForEachMeshTerm
from clusterer import Clusterer
from postprocessing import PostProcessing
from more_mesh_terms import MoreMeshTerms
from tagging_abstract import TaggingAbstract
# import more_mesh_terms
 
class App(QWidget):
	switch_window = QtCore.pyqtSignal(str)
	# moretermwindow = QtCore.pyqtSignal(str)
	def __init__(self):
		super().__init__()
		self.title = 'PUBMED database search'
		self.fileselected = 0
		self.fileName = ""
		self.rel_docs = []
		self.mesh_terms = []
		self.current_term_id = -1 # To keep current mesh term id
		self.current_index = 0 # To keep track of current window of result
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.showMaximized()
		p = self.palette()
		p.setColor(self.backgroundRole(), Qt.white)
		self.setPalette(p)	
		self.setStyleSheet('background-color: #263238')
		# Create grid
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.grid.setSpacing(0)
		
		# Search field
		self.searchbox = QLineEdit(self)
		self.searchbox.setText('breast cancer')
		self.searchbox.setStyleSheet('height: 30px; background-color: #CFD8DC')
		font = self.searchbox.font()      # lineedit current font
		font.setPointSize(14)               # change it's size
		self.searchbox.setFont(font)
		
		# Search button
		self.button = QPushButton('Search', self)
		self.button.setStyleSheet('padding: 7px; background-color: green')
		self.button.setCursor(Qt.PointingHandCursor)
		self.button.setToolTip('Search')
		self.button.clicked.connect(self.search_click)

		# Add first row to grid
		self.grid.addWidget(self.searchbox,0,0,1,5)
		self.grid.addWidget(self.button,0,5)

		# gene of docs select
		self.gene_button = QRadioButton("Relevant Genes")
		self.gene_button.setStyleSheet('color: black; background-color: violet');
		self.gene_button.setChecked(True)
		self.pmid_button = QRadioButton("Relevant PMID list ")
		self.pmid_button.setStyleSheet('color: black; background-color: violet');
		self.choose_file = QPushButton('Choose File')
		self.choose_file.setStyleSheet('padding: 4px; background-color: green')
		self.choose_file.setCursor(Qt.PointingHandCursor)
		self.choose_file.clicked.connect(self.chooseFile)
		self.filelabel = QLabel(self)
		self.filelabel.setStyleSheet('color: violet');

		# Add second row to grid
		self.grid.addWidget(self.gene_button,1,0,1,1)
		self.grid.addWidget(self.pmid_button,1,2,1,1)
		self.grid.addWidget(self.choose_file,1,3,1,1)
		self.grid.addWidget(self.filelabel,1,4,1,5)

		# Recommend label and Third row
		self.mtlabel = QLabel(' ')
		self.mtlabel.setStyleSheet('color: yellow');
		self.mtlabel.setFixedHeight(40)
		self.dummy = QLabel(' ')
		self.grid.addWidget(self.mtlabel,2,0)
		self.grid.addWidget(self.dummy,2,10)

		# Show best MeshTerms
		self.mt1 = QPushButton('')
		self.mt1.setStyleSheet('border: None; text-decoration: underline; color: violet')
		self.mt2 = QPushButton(' ')
		self.mt2.setStyleSheet('border: None; color: violet')

		# Add Fourth row to grid
		self.grid.addWidget(self.mt1,3,0,1,8)
		self.grid.addWidget(self.mt2,3,9)
		

		# Top result placeholder buttons
		self.title1 = QPushButton(' ')
		self.title1.setCursor(Qt.PointingHandCursor)
		# self.setToolTip("Click to see Tagged Entities")
		self.title1.setStyleSheet('text-align: left; border: None; padding-top: 40px; color: yellow')
		self.abs1 = QTextEdit(" ")
		self.abs1.setStyleSheet('text-align: left; border: None; color: white')
		self.abs1.setReadOnly(True)
		self.title2 = QPushButton(' ')
		self.title2.setCursor(Qt.PointingHandCursor)
		# self.setToolTip("Click to see Tagged Entities")
		self.title2.setStyleSheet('text-align: left; border: None; color: yellow')
		self.abs2 = QTextEdit(" ")
		self.abs2.setStyleSheet('text-align: left; border: None; color: white')
		self.abs2.setReadOnly(True)
		self.title3 = QPushButton(' ')
		self.title3.setCursor(Qt.PointingHandCursor)
		# self.setToolTip("Click to see Tagged Entities")
		self.title3.setStyleSheet('text-align: left; border: None; color: yellow')
		self.abs3 = QTextEdit(" ")
		self.abs3.setStyleSheet('text-align: left; border: None; color: white')
		self.abs3.setReadOnly(True)
		self.title4 = QPushButton(' ')
		self.title4.setCursor(Qt.PointingHandCursor)
		# self.setToolTip("Click to see Tagged Entities")
		self.title4.setStyleSheet('text-align: left; border: None; color: yellow')
		self.abs4 = QTextEdit(" ")
		self.abs4.setStyleSheet('text-align: left; border: None; color: white')
		self.abs4.setReadOnly(True)

		# Add Fourth row to grid
		self.grid.addWidget(self.title1,4,0,1,5)
		self.grid.addWidget(self.abs1,5,0,2,5)
		self.grid.addWidget(self.title2,8,0,1,5)
		self.grid.addWidget(self.abs2,9,0,2,5)
		self.grid.addWidget(self.title3,12,0,1,5)
		self.grid.addWidget(self.abs3,13,0,2,5)
		self.grid.addWidget(self.title4,16,0,1,5)
		self.grid.addWidget(self.abs4,17,0,2,5)

		# Visualization
		self.vizlabel = QPushButton(' ')
		self.vizlabel.setStyleSheet('text-align: left; border: None; padding-top: 40px; color: yellow')
		self.genecloud = QPushButton(' ')
		self.genecloud.setStyleSheet('text-align: left; border: None; text-decoration: underline; color: violet')
		self.meshcloud = QPushButton(' ')
		self.meshcloud.setStyleSheet('text-align: left; border: None; text-decoration: underline; color: violet')
		self.grid.addWidget(self.vizlabel,4,6)
		self.grid.addWidget(self.genecloud,5,6)
		self.grid.addWidget(self.meshcloud,6,6)

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
				clus = Clusterer(self.rel_docs,path,True,5)
				self.representative_id,self.representative,self.best_mesh_terms_id, self.best_mesh_terms = clus.cluster()
				if self.representative:
					self.updateRepresentativeInformation()
			else:
				print("Error! getting file name")
		elif self.pmid_button.isChecked():
			print("Golden corpus exists..")
		else:
			print("Please select related file..")
	def updateRepresentativeInformation(self):
		self.mtlabel.setText('Recommended search Term: ')
		self.mt1.setText(self.representative)
		self.mt1.clicked.connect(self.representative_click)
		self.mt1.setCursor(Qt.PointingHandCursor)
		self.mt2.setText('More Terms')
		self.mt2.setStyleSheet('border-width: 1px 1px; background-color: green; color: black')
		self.mt2.setCursor(Qt.PointingHandCursor)
		self.mt2.clicked.connect(self.more_meshterm_click)

		self.vizlabel.setText('Visualization: ')
		self.genecloud.setText('Genes cloud')
		self.genecloud.setCursor(Qt.PointingHandCursor)
		self.genecloud.clicked.connect(self.genecloud_clicked)
		self.meshcloud.setText('Mesh cloud')
		self.meshcloud.setCursor(Qt.PointingHandCursor)
		self.meshcloud.clicked.connect(self.meshcloud_clicked)
		# update term tagging
		pp = PostProcessing()
		tags = pp.term_tagging(self.best_mesh_terms)
		self.tags = QPushButton('Tags:')
		self.tags.setStyleSheet('text-align: left; border: None; padding-top: 40px; color: yellow')
		self.grid.addWidget(self.tags,7,6)
		row = 8
		col = 6
		# update tag fields on clicking representative
		if tags:
			for _k, _v in tags:
				self.grid.addWidget(TagButton(_k),row,col)
				row += 1
		else:
			print("No tags!")

	def representative_click(self):
		if self.representative_id:
			self.previous = QPushButton()
			self.previous.setStyleSheet('border: None')
			self.previous.clicked.connect(self.previous_clicked)
			self.grid.addWidget(self.previous,16,6)
			self.next = QPushButton("Next->")
			self.next.setStyleSheet('background-color: green')
			self.next.setCursor(Qt.PointingHandCursor)
			self.next.clicked.connect(self.next_clicked)
			self.grid.addWidget(self.next,16,7)

			self.current_term_id = self.representative_id
			self.populateTitleAbs(self.representative_id)

	def populateTitleAbs(self,json_no):
		if json_no:
			self.current_term_id = json_no
			pp = PostProcessing()
			titles , abstracts, sameabs = pp.getTitleAbs(self.current_index,json_no,self._search_term)
			if titles and abstracts:
				self.title1.setText(titles[0])
				self.title1.clicked.connect(lambda: self.title_clicked(sameabs[0]))
				self.title2.setText(titles[1])
				self.title2.clicked.connect(lambda: self.title_clicked(sameabs[1]))
				self.title3.setText(titles[2])
				self.title3.clicked.connect(lambda: self.title_clicked(sameabs[2]))
				self.title4.setText(titles[3])
				self.title4.clicked.connect(lambda: self.title_clicked(sameabs[3]))
				self.abs1.setText(abstracts[0])
				self.abs2.setText(abstracts[1])
				self.abs3.setText(abstracts[2])
				self.abs4.setText(abstracts[3])

	def title_clicked(self, abstract):
		self.switch_window.emit(abstract)
		self.switch_window.connect(self.show_tag_window)

	def show_tag_window(self, abstract):
		# print(abstract)
		self.pop = TaggingAbstract(abstract)
		self.pop.show()

	def next_clicked(self):
		self.current_index = self.current_index + 1
		self.populateTitleAbs(self.current_term_id)
		self.previous.setText("<-Previous")
		self.previous.setStyleSheet('padding: 3px; background-color: green')
		self.previous.setCursor(Qt.PointingHandCursor)
	
	def previous_clicked(self):
		self.current_index = self.current_index - 1
		if self.current_index >= 0:
			self.populateTitleAbs(self.current_term_id)
		else:
			self.previous.setText('')
			self.previous.setStyleSheet('border: None')
			self.current_index = -1

	def more_meshterm_click(self):
    	# Must write [self.parent] not [parent]
		self.parent = QMainWindow()
		self.popup = MoreMeshTerms(self,self.parent,self.best_mesh_terms,self.best_mesh_terms_id)
		# self.popup.setupUi(self,self.parent,self.best_mesh_terms,self.best_mesh_terms_id)
		self.parent.show()

	def genecloud_clicked(self):
		_textval = self.searchbox.text()
		postprocessing = PostProcessing()
		if(self.current_term_id >= 0 and len(self.fileName) and len(_textval)):
			postprocessing.gene_cloud(self.current_term_id,self.fileName,_textval)

	def meshcloud_clicked(self):
		_textval = self.searchbox.text()
		postprocessing = PostProcessing()
		if(self.current_term_id >= 0 and len(_textval)):
			postprocessing.mesh_cloud(self.current_term_id,_textval)


	def chooseFile(self): 
		if self.fileselected:
			self.filelabel.setText("")
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		self.fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
		if self.fileName:
			self.filelabel.setText(self.fileName)
			self.fileselected = 1;
	
class TagButton(QPushButton):
	def __init__(self,term):
		super(TagButton, self).__init__()
		self.setText(term)
		self.setStyleSheet('text-align: left; border: None; color: violet')

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())
