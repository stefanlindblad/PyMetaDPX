#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DPX Editing Tool for SMPTE Timecodes
# Created by Stefan Seibert under MIT License 
# in 2013 at Stuttgart Media University

# first version, only for editing smpte timecodes,
# more functions will follow later.

import sys, struct
from PyQt4 import QtCore, QtGui

class MainWindow(QtGui.QMainWindow):

  editedFiles = 0
	timecode = "00:00:56:00"
	framerate = "25"
	filename = ""

	def __init__(self, *args):
		QtGui.QMainWindow.__init__(self, *args)
		self.createMenu()
		self.createComponents()
		self.createLayout()
		self.createConnects()
		
		self.setWindowTitle(self.tr(u"DPX Editing Tool for SMPTE Timecodes"))
		self.resize(600, 400)
		self.setMinimumSize(600,  400)
		self.setMaximumSize(600,  400)
		
	def createMenu(self):
		self.actionOpenFile = QtGui.QAction(self.tr("Select File or Sequence"), self)
		self.exit = QtGui.QAction(self.tr("Quit"), self)
		self.exit.setMenuRole(QtGui.QAction.QuitRole)
		self.about = QtGui.QAction(self.tr("About and Help"), self)
		
		menuFile = self.menuBar().addMenu(self.tr("File"))
		menuFile.addAction(self.actionOpenFile)
		menuFile.addSeparator()
		menuFile.addAction(self.about)
		menuFile.addSeparator()
		menuFile.addAction(self.exit)
		
	@QtCore.pyqtSlot()
	def showAboutDialog(self):
		QtGui.QMessageBox.information(self, u"42", u"This Tool was created at Stuttgart Media University in 2013 by Stefan Seibert. Just choose a dpx file or sequence in the file menu and the tool will show the current SMPTE timecode. You can then change the timecode and/or the framerate. It will then change all files in the sequence, beginning at the selected file. For Questions please contact hdm-support@stefanseibert.com")

	@QtCore.pyqtSlot()
	def exitApp(self):
		self.close()
	
	@QtCore.pyqtSlot()
	def getFileName(self):
		self.filename = QtGui.QFileDialog.getOpenFileName(self, u"Choose Files", QtCore.QDir.currentPath(), u"DPX Files (*.dpx)")
		
		if not self.filename == "":
			self.filename = unicode(self.filename)
			self.fieldFile.insert(format(self.filename))
		
	@QtCore.pyqtSlot()
	def editSequence(self):
		self.framerate = self.fieldFrameRate.text()
		self.timecode = self.fieldTimeCode.text()
		
		if (self.filename == "") or (self.framerate == "") or (self.timecode == ""):
			QtGui.QMessageBox.warning(self, u"Error!", u"Missing Timecode, File or Framerate!")
			
		else:
			file = self.filename[:-4]
			ending = ".dpx"
			frameNumberLength = self.findFrameNumberLength(file)
			path = file[:-frameNumberLength]
			startFrame = file[-frameNumberLength:]
			finished = False
			counter = 0
	
			
			while finished == False:
				
				try:
					thisFrame = int(startFrame) + counter
					name = path + self.fillIt(str(thisFrame), frameNumberLength) + ending
					self.writeTC(name)
					self.timecode = self.incrementTC(self.timecode)
					counter += 1
					
				
				except IOError:
					QtGui.QMessageBox.information(self, u"23", u"I am done, thanks for waiting.")
					finished = True;

		
		
	def incrementTC(self, tc):
		
		fr = self.framerate
		
		hour = int(tc[0:2])
		minute = int(tc[3:5])
		second = int(tc[6:8])
		frame = int(tc[-2:])
		
		frame += 1
		
		if(frame >= int(fr)):
			frame = 0
			second += 1
			
		if(second > 59):
			second = 0
			minute += 1
			
		if(minute > 59):
			minute = 0
			hour += 1
			
		if(hour > 23):
			frame = 0
			second = 0
			minute = 0
			hour = 0
			
		return self.fillIt(str(hour), 2) + ":" + self.fillIt(str(minute), 2) + ":" + self.fillIt(str(second), 2) + ":" + self.fillIt(str(frame), 2)
		
	
	def findFrameNumberLength(self, input):
	
		input2 = input
		found = False
		length = 0
		
		while found == False:
			if (input2[-1:] == "0") or (input2[-1:] == "1") or (input2[-1:] == "2") or (input2[-1:] == "3") or (input2[-1:] == "4") or (input2[-1:] == "5") or (input2[-1:] == "6") or (input2[-1:] == "7") or (input2[-1:] == "8") or (input2[-1:] == "9"):
				length += 1
				input2 = input2[:-1]
			
			else:
				found = True
				return length
		
	def createComponents(self):
		self.labelSelected = QtGui.QLabel(self.tr(u"Selected File: (make sure that the last digits before \".dpx\" are the frame count)"))
		self.labelFrameRate = QtGui.QLabel(self.tr(u"Framerate: (This field is required, only integer values like 24, 25 etc. are allowed)"))
		self.labelTimeCode = QtGui.QLabel(self.tr(u"Timecode: (in the following format: \"HH:MM:SS:FF\")"))
		self.labelInfo1 = QtGui.QLabel(self.tr(u" "))
		self.labelInfo3 = QtGui.QLabel(self.tr(u" "))
		self.labelInfo2 = QtGui.QLabel(self.tr(u"Closing the Application without waiting for the final dialog can result in unexpected behaviours and data damage!"))
		self.labelInfo2.setAlignment(QtCore.Qt.AlignCenter)
		self.updateButton = QtGui.QPushButton(self.tr(u"Edit!"))
		self.fieldFile = QtGui.QLineEdit()
		self.fieldFile.setReadOnly(True)
		self.fieldFrameRate = QtGui.QLineEdit(self.framerate)
		self.fieldFrameRate.setMaxLength(2)
		self.logOutput = QtGui.QTextEdit()
		self.logOutput.setReadOnly(True)
		self.logOutput.setLineWrapMode(QtGui.QTextEdit.NoWrap);
		
		self.fieldTimeCode = QtGui.QLineEdit(self.timecode)
		self.fieldTimeCode.setMaxLength(11)
		
	def createConnects(self):
		self.actionOpenFile.triggered.connect(self.getFileName)
		self.about.triggered.connect(self.showAboutDialog)
		self.exit.triggered.connect(self.exitApp)
		self.updateButton.clicked.connect(self.editSequence)
		
	def createLayout(self):
		layoutCentral = QtGui.QVBoxLayout()
		layoutCentral.addWidget(self.labelSelected)
		layoutCentral.addWidget(self.fieldFile)
		layoutCentral.addWidget(self.labelTimeCode)
		layoutCentral.addWidget(self.fieldTimeCode)
		layoutCentral.addWidget(self.labelFrameRate)
		layoutCentral.addWidget(self.fieldFrameRate)
		layoutCentral.addWidget(self.labelInfo3)
		layoutCentral.addWidget(self.updateButton)
		layoutCentral.addWidget(self.labelInfo1)
		layoutCentral.addWidget(self.labelInfo2)
		layoutCentral.addWidget(self.logOutput)
		
		widgetCentral = QtGui.QWidget()
		widgetCentral.setLayout(layoutCentral)
		self.setCentralWidget(widgetCentral)
		
	# transforms decimal number representation in 4 byte binarys
	def dec2bin(self, value):
		if str(value) == '0':
			return '0000'
		elif str(value) == '1':
			return '0001'
		elif str(value) == '2':
			return '0010'
		elif str(value) == '3':
			return '0011'
		elif str(value) == '4':
			return '0100'
		elif str(value) == '5':
			return '0101'
		elif str(value) == '6':
			return '0110'
		elif str(value) == '7':
			return '0111'
		elif str(value) == '8':
			return '1000'
		elif str(value) == '9':
			return '1001'
		else:
			return '0000'
	
	# transforms 4 byte binary numbers in decimal numbers
	def bin2dec(self, value):
		if str(value) == '0000':
			return '0'
		elif str(value) == '0001':
			return '1'
		elif str(value) == '0010':
			return '2'
		elif str(value) == '0011':
			return '3'
		elif str(value) == '0100':
			return '4'
		elif str(value) == '0101':
			return '5'
		elif str(value) == '0110':
			return '6'
		elif str(value) == '0111':
			return '7'
		elif str(value) == '1000':
			return '8'
		elif str(value) == '1001':
			return '9'
		else:
			return '0000'
	
	# fills a binary string with zeros until maximum size
	def fillIt(self, input, max):
		
		if input.__len__() < max:
			return "0" + self.fillIt(input, max-1)	
		else:
			return input
	
	# translates a given decimal number into readable timecode string
	def value2tc(self, input):
	
		inputString = str(bin(input))
		inputString = inputString[2:]
		inputString = self.fillIt(inputString, 32)
	
		GH = self.bin2dec(inputstring3[0:4])
		KH = self.bin2dec(inputstring3[4:8])
		GM = self.bin2dec(inputstring3[8:12])
		KM = self.bin2dec(inputstring3[12:16])	
		GS = self.bin2dec(inputstring3[16:20])
		KS = self.bin2dec(inputstring3[20:24])
		GF = self.bin2dec(inputstring3[24:28])
		KF = self.bin2dec(inputstring3[-4:])
	
		if (GH or KH or GM or KM or GS or KS or GF or KF > 9) or (GH or KH or GM or KM or GS or KS or GF or KF < 0):
			QtGui.QMessageBox.warning(self, u"Wrong value2tc!", u"The given Framerate or Timecode are not in the correct format!")
	
		else:	
			value = GH + KH + ":" + GM + KM + ":" + GS + KS + ":" + GF + KF
			return value
	
	# translates a given timecode string into decimal number	
	def tc2value(self, input):
		hour = int(input[0:2])
		minute = int(input[3:5])
		second = int(input[6:8])
		frame = int(input[-2:])
	
		if hour > 9:
			bH = hour / 10
			lH = hour % 10
			value = self.dec2bin(bH) + self.dec2bin(lH)
		else:
			bH = 0
			lH = hour
			value = self.dec2bin(bH) + self.dec2bin(lH)
			
		if minute > 9:
			bM = minute / 10
			lM = minute % 10
			value = value + self.dec2bin(bM) + self.dec2bin(lM)
		else:
			bM = 0
			lM = minute
			value = value + self.dec2bin(bM) + self.dec2bin(lM)
			
		if second > 9:
			bS = second / 10
			lS = second % 10
			value = value + self.dec2bin(bS) + self.dec2bin(lS)
		else:
			bS = 0
			lS = second
			value = value + self.dec2bin(bS) + self.dec2bin(lS)
			
		if frame > 9:
			bF = frame / 10
			lF = frame % 10
			value = value + self.dec2bin(bF) + self.dec2bin(lF)
		else:
			bF = 0
			lF = frame
			value = value + self.dec2bin(bF) + self.dec2bin(lF)
			
		return value

	
	# writes a given timecode(readable string) into a given file
	def writeTC(self, file):
		fp = open(file, 'r+b')
		endian = fp.read(4)
		tc = self.timecode
		tcBin = self.tc2value(tc)
		tcDec = int(str(tcBin),2)
		self.logOutput.insertPlainText("File: " + file)
		self.logOutput.insertPlainText( ", Timecode: " + tc)
		#self.logOutput.insertPlainText( "Writing Timecode Binary: " + tcBin)
		#self.logOutput.insertPlainText( "Writing Timecode Decimal: " + str(tcDec))
		self.logOutput.insertPlainText("\r\n")
	
		if endian == "SDPX":
			fp.seek(1920)
			fp.write(struct.pack('>I', tcDec))
			fp.close()
			self.editedFiles += 1
			
		else:
			QtGui.QMessageBox.warning(self, u"Wrong Endianess!", u"Sorry, currently are only Little Endian Systems supported(x86) - Please exit!")


		

def main(argv):
	app = QtGui.QApplication(argv)
	mainwindow = MainWindow()
	mainwindow.show()
	sys.exit(app.exec_())
	
if __name__ == "__main__":
	main(sys.argv)
