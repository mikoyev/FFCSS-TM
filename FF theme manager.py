from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QRect
from PyQt5 import QtWidgets, QtGui
import sys, sqlite3, os, shutil
import csv
import time
from random import randint


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   STRIKE = '\u0336'
   CONCEAL='\033[8m'
   CROSSED='\033[9m'
   END = '\033[0m'

class App(QMainWindow):
    "main window"

    def __init__(self, Parent = None):
        'initializer'
        super(App, self).__init__()

        self.title = 'Firefox CSS Theme Manager'
        self.resize(1000, 500)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setCentralWidget(QWidget(self))

        #this is here for readability bc pylint is an ass
        self.maingroupbox = None
        self.topgroupbox = None
        self.themelist = None
        self.saved = False
        self.loadedtheme = "None"
        self.textselected = "None"

        self.paththemes = ""
        self.pathprofile = ""

        self.themebutton="theme"
        self.themes = ["Vanilla Theme"]

        os.chdir(os.path.dirname(os.path.realpath(__file__))) #change working directory to script location

        self.initUI()

    def closeEvent(self, event):
        
        if self.saved==True:
            event.accept()
        else:
            os.remove("FFTMdb.db")
            event.accept()

    def initUI(self):
        
        self.setWindowTitle(self.title)        
    
        self.createtop()
        self.createmain()

        mainlayout = QVBoxLayout()
        mainlayout.addWidget(self.topgroupbox)
        mainlayout.addWidget(self.maingroupbox)
        #self.centralWidget().setLayout(mainlayout)
        self.centralWidget().setLayout(mainlayout)
        self.show()

        self.checkprofile()
        self.dbcheck()
        self.loadfiles()
        
        
    def choosethemesfolder(self):
        
        self.paththemes = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Themes Folder')
        if self.paththemes != "":
            self.themefolderindicator.setText(self.paththemes)
            self.loadfiles()

    def chooseprofilefolder(self):
        
        self.pathprofile = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Profile Folder')
        if self.pathprofile != "":
            self.profilefolderindicator.setText(self.pathprofile)
            self.checkprofile()

    def loadfiles(self):

        if self.paththemes != "":
            self.themes.clear()
            self.themes.append("Vanilla Theme")
            filelist = os.listdir(self.paththemes)
            for i in range(len(filelist)):
                self.themes.append(filelist[i])
        
            self.themelist.clear()
            self.themelist.addItems(self.themes)
        else:
            pass
    
    def checkprofile(self):

        if os.path.isdir(self.pathprofile+r"\chrome") is True:
            self.labelchromepresent.setText("🟢 Chrome folder is present")

            if len(os.listdir(self.pathprofile+r"\chrome")) == 0:
                self.loadedtheme="Vanilla Theme"
                self.labelloaded.setText("Loaded theme:\n\n"+self.loadedtheme)
                self.labelchromestate.setText("🔴 Chrome folder is empty")
            else:    
                self.labelchromestate.setText("🟢 Chrome folder is not empty")

        else:
            self.labelchromepresent.setText("🔴 Chrome folder is not present")
            self.labelchromestate.setText("🔴 Chrome folder is not present")

        if os.path.isfile(self.pathprofile+r"\user.js") is True:
            self.labeljspresent.setText("🟢 User.js is present")
        else:
            self.labeljspresent.setText("🔴 User.js not present")

    def createdb(self):

        conn=sqlite3.connect('FFTMdb.db')
        c=conn.cursor()

        c.execute("""CREATE TABLE db(
                    name text,
                    data text)
                    """)


        baseinfo= [("themepath", ""), ("profilepath", ""), ("currenttheme", "")]

        c.executemany("INSERT INTO db VALUES (?,?)", baseinfo)

        conn.commit()
        conn.close()

    
    def dbcheck(self):

        if os.path.isfile('FFTMdb.db') is False:
            
            self.createdb()

        else:
            conn=sqlite3.connect('FFTMdb.db')
            c=conn.cursor()
            c.execute("SELECT * FROM db")
            a=c.fetchall()

            if a[0][0]=="themepath" and a[1][0]=="profilepath" and a[2][0]=="currenttheme":

                self.paththemes = a[0][1]
                self.pathprofile = a[1][1]
                self.loadedtheme = a[2][1]
                self.labelloaded.setText("Loaded theme:\n\n"+self.loadedtheme)

                self.themefolderindicator.setText(self.paththemes)
                self.profilefolderindicator.setText(self.pathprofile)

                

                self.saved=True
                conn.close()

            else:
                conn.close()

                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText("Database corrupted.")
                msgBox.setInformativeText("Creating new file.")
                msgBox.setWindowTitle("Database Error")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort )

                result = msgBox.exec_()
                if result == QMessageBox.Ok:
                    pass
                else:
                    app = QApplication.instance()
                    app.closeAllWindows()

                os.remove("FFTMdb.db")
                self.createdb()


    def changetheme(self):

        cfolder=False
        dst=self.pathprofile
        profilefilelist = os.listdir(self.pathprofile)

        if self.textselected == "Vanilla Theme":

            for i in range(len(profilefilelist)):
                if profilefilelist[i] == "chrome": #if chrome exists in profile
                        shutil.rmtree(dst+"\\chrome")
                else:
                    pass

                if profilefilelist[i] == "user.js": #if userjs exists in profile
                    os.remove(dst+"\\user.js")
                else:
                    pass

        else:

            #check if chrome folder is present in the theme
            
            src=self.paththemes + "\\" + self.textselected
            themefilelist = os.listdir(src)
            
            for i in range(len(themefilelist)):

                if themefilelist[i] == "chrome": #if chrome exists
                    src=self.paththemes + "\\" + self.textselected + "\\chrome"
                    dst=self.pathprofile + "\\chrome"

                    cfolder=True
                    for j in range(len(profilefilelist)):
                        if profilefilelist[j] == "chrome": #if chrome exists in profile
                            shutil.rmtree(dst)
                        else:
                            pass

                    shutil.copytree(src, dst)

                else: #if chrome not exists
                    pass
                    
                if themefilelist[i] == "user.js": #if usejs exists

                    src=self.paththemes + "\\" + self.textselected + "\\user.js"
                    dst=self.pathprofile + "\\user.js"

                    for j in range(len(profilefilelist)):
                        if profilefilelist[j] == "user.js": #if userjs exists in profile
                            os.remove(dst)
                        else:
                            pass

                    shutil.copy2(src, dst)

                else:
                    pass

            if cfolder==False:

                src=self.paththemes + "\\" + self.textselected
                dst=self.pathprofile 

                for i in range(len(profilefilelist)):
                        if profilefilelist[i] == "chrome": #if chrome exists in profile
                            print(dst)
                            shutil.rmtree(dst+"\\chrome")
                        else:
                            pass

                        if profilefilelist[i] == "user.js": #if userjs exists in profile
                            os.remove(dst+"\\user.js")
                        else:
                            pass

                shutil.copytree(src, dst+"\\chrome")

            #if yes copy it to path
            #else copy everything to chrome
            #check if user.js is present
            #if yes copy it

            #shutil.copytree(src, dst)


    def savedata(self):

        if self.textselected == "None":
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("No theme selected.")
            msgBox.setInformativeText("Please select a theme.")
            msgBox.setWindowTitle("Theme Selection Error")
            #msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort )

            msgBox.exec_()

        else:

            self.applybutton.setText("Applying Theme")
            self.applybutton.setEnabled(False)
            

            self.changetheme()

            conn=sqlite3.connect('FFTMdb.db')
            c=conn.cursor()

            c.execute("""UPDATE db 
                        SET data = ?
                        WHERE name = 'themepath'
                    """, (self.paththemes,))

            c.execute("""UPDATE db SET 
                        data = ?
                        WHERE name = 'profilepath'
                    """, (self.pathprofile,))
                        
            c.execute("""UPDATE db SET 
                        data = ?
                        WHERE name = 'currenttheme'
                    """, (self.textselected,))

                        
            conn.commit()
            conn.close()

            self.loadedtheme=self.textselected
            self.labelloaded.setText("Loaded theme:\n\n"+self.loadedtheme)
            self.saved=True
            self.checkprofile()

            self.applybutton.setText("Apply selected profile")
            self.applybutton.setEnabled(True)
            

    def createtop(self):

        self.topgroupbox = QGroupBox()
        layout = QHBoxLayout()

        themefolderchooser = QPushButton("Select themes folder")
        themefolderchooser.setStyleSheet("padding-left: 15px; padding-right: 15px; padding-top: 8px; padding-bottom: 8px;");
        themefolderchooser.clicked.connect(self.choosethemesfolder)

        profilefolderchooser = QPushButton("Select profile folder")
        profilefolderchooser.setStyleSheet("padding-left: 15px; padding-right: 15px; padding-top: 8px; padding-bottom: 8px;");
        profilefolderchooser.clicked.connect(self.chooseprofilefolder)


        themefolderpath = self.paththemes
        self.themefolderindicator = QLabel(themefolderpath, self) #the self needs to be there or else it will crash
        self.themefolderindicator.setMinimumWidth(32)

        profilefolderpath = self.pathprofile
        self.profilefolderindicator = QLabel(profilefolderpath, self)

        #self.progress = QProgressBar()
        #self.progress.setStyleSheet("padding-left: 0px; padding-right: 0px; padding-top: 0px; padding-bottom: 0px;");
        #self.progress.setContentsMargins(0,10,0,10)
        #self.progress.setFixedWidth(250)


        layout.addWidget(themefolderchooser)
        layout.addWidget(self.themefolderindicator)
        layout.addSpacing(30)
        layout.addWidget(profilefolderchooser)
        layout.addWidget(self.profilefolderindicator)
        layout.addSpacing(40)
        layout.addStretch(1)
        #layout.addWidget(self.progress)
        self.topgroupbox.setFixedHeight(60)
        self.topgroupbox.setLayout(layout)

    def select(self):
        
        if self.themelist.currentRow() > 0:
            self.textselected= self.themes[self.themelist.currentRow()]
        else:
            self.textselected= self.themes[0]

        self.labelselected.setText("Selected theme:\n\n"+self.textselected)

    def createmain(self):

        self.maingroupbox = QGroupBox()
        layout = QHBoxLayout()

        leftbox=QFrame()
        leftbox.setFixedWidth(200)
        leftboxlayout=QVBoxLayout()

        statusbox=QGroupBox()
        statustboxlayout=QVBoxLayout()
    
        self.themelist = QListWidget()
        self.themelist.addItems(self.themes)

        layout.addWidget(leftbox)
        layout.addWidget(self.themelist)

        self.labelloaded = QLabel("Loaded theme:\n\n"+self.loadedtheme)
        self.labelloaded.setAlignment(Qt.AlignCenter)
        self.labelselected = QLabel("Selected theme:\n\n"+self.textselected)
        self.labelselected.setAlignment(Qt.AlignCenter)
        self.applybutton = QPushButton("Apply selected profile")
        self.applybutton.clicked.connect(self.savedata)
        

        self.themelist.currentRowChanged.connect(lambda: self.select())


        self.labelchromepresent = QLabel("🟢 Chrome folder present")
        self.labelchromestate = QLabel("🔴 Chrome folder empty")
        self.labeljspresent = QLabel("🟢 User.js is present")

        statustboxlayout.addSpacing(10)
        statustboxlayout.addWidget(self.labelchromepresent)
        statustboxlayout.addSpacing(5)
        statustboxlayout.addWidget(self.labelchromestate)
        statustboxlayout.addSpacing(5)
        statustboxlayout.addWidget(self.labeljspresent)
        statustboxlayout.addSpacing(10)

        leftboxlayout.addWidget(statusbox)
        leftboxlayout.addSpacing(30)
        leftboxlayout.addWidget(self.labelloaded)
        leftboxlayout.addSpacing(30)
        leftboxlayout.addWidget(self.labelselected)
        leftboxlayout.addSpacing(40)
        leftboxlayout.addStretch(1)
        leftboxlayout.addWidget(self.applybutton)
        

        statusbox.setLayout(statustboxlayout)
        leftbox.setLayout(leftboxlayout)
        self.maingroupbox.setLayout(layout)
        

if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec_())
