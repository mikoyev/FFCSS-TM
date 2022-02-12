from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import QtWidgets, QtGui
import sys, sqlite3, os, shutil, zipfile
from PyQt5.QtWebEngineWidgets import *

class App(QMainWindow):
    "main window"
    paththemes = ""
    themelist = None
    def __init__(self, parent=None):
        'initializer'
        super(App, self).__init__(parent)

        self.tb=None
        self.title = 'Firefox CSS Theme Manager'
        self.resize(1000, 500)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setCentralWidget(QWidget(self))

        #this is here for readability bc pylint is an ass
        self.maingroupbox = None
        self.topgroupbox = None
        #self.themelist = None
        self.saved = False
        self.infoopen=False
        self.loadedtheme = "None"
        self.textselected = "None"
        self.d= "None"

        #self.paththemes = ""
        self.pathprofile = ""

        self.themebutton="theme"
        self.themes = ["Vanilla Theme"]
        self.green = '<font color="green">✔️</font>'
        self.red = '<font color="red">✖️</font>'

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

        self.dbcheck()
        self.checkprofile()
        self.loadfiles()
        
        
    def choosethemesfolder(self):
        
        self.paththemes = os.path.normpath(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Themes Folder'))
        if self.paththemes != "":
            self.themefolderindicator.setText(self.paththemes)
            self.loadfiles()

    def chooseprofilefolder(self):
        
        self.pathprofile = os.path.normpath(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Profile Folder'))
        if self.pathprofile != "":
            self.profilefolderindicator.setText(self.pathprofile)
            self.checkprofile()

    def loadfiles(self):

        if self.paththemes != "":
            self.themes.clear()

            for f in os.listdir(self.paththemes): #appends full path
                if os.path.isdir(os.path.join(self.paththemes, f)):
                    self.themes.append(os.path.join(self.paththemes, f))

            self.themes.sort(key=os.path.getmtime) #sort by time (full path necessary)

            for i, t in enumerate(self.themes):
                self.themes[i]=t.split(os.path.sep)[-1]

            self.themes.insert(0, "Vanilla Theme")

            self.themelist.clear()
            self.themelist.addItems(self.themes)
            
        else:
            pass
    
    def checkprofile(self):


        if os.path.isdir(os.path.join(self.pathprofile, "chrome")) is True:
            self.labelchromepresent.setText(self.green + " Chrome folder is present")

            if len(os.listdir(os.path.join(self.pathprofile, "chrome"))) == 0:
                self.loadedtheme="Vanilla Theme"
                self.labelloaded.setText("Loaded theme:\n\n"+self.loadedtheme)
                self.labelchromestate.setText(self.red + " Chrome folder is empty")
            else:    
                self.labelchromestate.setText(self.green + " Chrome folder is not empty")

        else:
            self.labelchromepresent.setText(self.red + " Chrome folder is not present")
            self.labelchromestate.setText(self.red + " Chrome folder is not present")

        if os.path.isfile(os.path.join(self.pathprofile, "user.js")) is True:
            self.labeljspresent.setText(self.green + " User.js is present")
        else:
            self.labeljspresent.setText(self.red + " User.js not present")

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

                self.paththemes = os.path.normpath(a[0][1])
                self.pathprofile = os.path.normpath(a[1][1])
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
                        shutil.rmtree(os.path.join(dst, "chrome"))
                else:
                    pass

                if profilefilelist[i] == "user.js": #if userjs exists in profile
                    os.remove(os.path.join(dst, "user.js"))
                else:
                    pass

        else:

            #check if chrome folder is present in the theme
            
            src=os.path.join(self.paththemes, self.textselected)

            themefilelist = os.listdir(src)
            
            for i in range(len(themefilelist)):

                if themefilelist[i] == "chrome": #if chrome exists
                    src=os.path.join(self.paththemes, self.textselected, "chrome")
                    dst=os.path.join(self.pathprofile, "chrome")

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

                    src=os.path.join(self.paththemes, self.textselected, "user.js")
                    dst=os.path.join(self.pathprofile, "user.js")

                    for j in range(len(profilefilelist)):
                        if profilefilelist[j] == "user.js": #if userjs exists in profile
                            os.remove(dst)
                        else:
                            pass

                    shutil.copy2(src, dst)

                else:
                    pass

            if cfolder==False:

                src=os.path.join(self.paththemes, self.textselected)
                dst=self.pathprofile 

                for i in range(len(profilefilelist)):
                        if profilefilelist[i] == "chrome": #if chrome exists in profile
                            shutil.rmtree(os.path.join(dst, "chrome"))
                        else:
                            pass

                        if profilefilelist[i] == "user.js": #if userjs exists in profile
                            os.remove(os.path.join(dst, "user.js"))
                        else:
                            pass

                shutil.copytree(src, os.path.join(dst, "chrome"))

            #if yes copy it to path
            #else copy everything to chrome
            #check if user.js is present
            #if yes copy it


    def savedata(self):

        if self.textselected == "None":
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("No theme selected.")
            msgBox.setInformativeText("Please select a theme.")
            msgBox.setWindowTitle("Theme Selection Error")
            msgBox.adjustSize()
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
            
    def infoclose(self, event):

        self.infoopen=False

    def infobox(self):

        """Regarding the infobox not showing with .show(): What seems to be happening is that 
        you define  local variable d and initialize it as a QDialog, then show it. The problem 
        is that once the buttonPressed handler is finished executing, the reference to d goes 
        out of scope, and so it is destroyed by the garbage collector."""

        if self.infoopen==False:
            self.d = QDialog(self, Qt.WindowTitleHint | Qt.WindowCloseButtonHint) #first adds title, seconds adds close button, done to remove the help button
            self.d.setWindowTitle("Information")

            layout = QGridLayout()

            info1=QLabel("Usual location of Firefox profile (also available on Firefox's \"about:profiles\" page):\n\n" 
            +r"     ▶   Linux - $HOME/.mozilla/firefox/XXXXXXX.default-XXXXXX"+"\n"
            +r"     ▶   Windows 10 - C:\Users\<USERNAME>\AppData\Roaming\Mozilla\Firefox\Profiles\XXXXXXX.default-XXXXXX"+"\n"
            ,self.d)

            info2=QLabel("Enable these on Firefox's \"about:config\" page:\n\n     ▶   toolkit.legacyUserProfileCustomizations.stylesheets\n     ▶   layers.acceleration.force-enabled\n     ▶   gfx.webrender.all\n     ▶   gfx.webrender.enabled\n     ▶   layout.css.backdrop-filter.enabled\n     ▶   svg.context-properties.content.enabled"
            ,self.d)

            extrainfo=QLabel("<a href=\"https://github.com/FirefoxCSS-Store/FirefoxCSS-Store.github.io/blob/main/README.md#generic-installation\"> More info </a>", self.d)
            #extrainfo.setTextFormat(Qt.RichText)
            extrainfo.setOpenExternalLinks(True)
            extrainfo.setToolTip("https://github.com/FirefoxCSS-Store/FirefoxCSS-Store.github.io/blob/main/README.md#generic-installation")

            layout.addWidget(info1, 0, 0, 1, 0)
            layout.addWidget(info2, 1, 0)
            layout.addWidget(extrainfo, 1, 1, alignment=Qt.AlignRight | Qt.AlignBottom) # | combines multiple aligment rules

            self.d.setLayout(layout)

            self.d.setWindowModality(Qt.NonModal)
            self.d.show()
            self.infoopen=True
            self.d.closeEvent = self.infoclose
        else:
            qtRectangle = self.frameGeometry()
            self.d.move(qtRectangle.center())
            self.d.activateWindow()
    
    def showthemebrowser(self, event):
        if self.tb is None:
            self.tb = ThemeBrowser()
        self.tb.show()

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
        #self.themefolderindicator.setMinimumWidth(32)

        profilefolderpath = self.pathprofile
        self.profilefolderindicator = QLabel(profilefolderpath, self)

        infobutton = QPushButton("❓️")
        infobutton.setFixedSize(30,30)
        
        infobutton.clicked.connect(self.infobox)


        layout.addWidget(themefolderchooser)
        layout.addWidget(self.themefolderindicator)
        layout.addSpacing(20)
        layout.addWidget(profilefolderchooser)
        layout.addWidget(self.profilefolderindicator)
        layout.addSpacing(40)
        layout.addStretch(1)
        layout.addWidget(infobutton)

        self.topgroupbox.setFixedHeight(50)
        self.topgroupbox.setLayout(layout)

    def select(self):
        
        if self.themelist.currentRow() > 0:
            self.textselected = self.themes[self.themelist.currentRow()]
        else:
            self.textselected = self.themes[0]

        self.labelselected.setText("Selected theme:\n\n"+self.textselected)

    def createmain(self):

        self.maingroupbox = QGroupBox()
        layout = QHBoxLayout()

        leftbox=QFrame()
        #leftbox.setFixedWidth(200)
        leftbox.adjustSize() #fits size to content!
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

        themesinfo=QLabel('<a href="/">Theme Collection</a>')
        themesinfo.setTextInteractionFlags(Qt.TextSelectableByMouse)
        themesinfo.mousePressEvent = self.showthemebrowser
        #themesinfo.setTextFormat(Qt.RichText)
        themesinfo.setOpenExternalLinks(True)
        themesinfo.setToolTip("https://firefoxcss-store.github.io/")
        themesinfo.setAlignment(Qt.AlignCenter)


        self.themelist.currentRowChanged.connect(lambda: self.select())


        self.labelchromepresent = QLabel("Initializing...")
        self.labelchromestate = QLabel("Initializing...")
        self.labeljspresent = QLabel("Initializing...")
 
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
        leftboxlayout.addSpacing(5)
        leftboxlayout.addWidget(themesinfo)

        statusbox.setLayout(statustboxlayout)
        leftbox.setLayout(leftboxlayout)
        self.maingroupbox.setLayout(layout)

class ThemeBrowser(QWidget):

    def downloadRequested(self, download):

            downloadpath = download.path()

            filename=downloadpath.split(os.path.sep)[-1] #use OS separator instead of /
            self.foldername=filename.split('.')[1]
            

            if self.folderpath!="":
                self.fpath = os.path.join(self.folderpath, filename) #if theres theme folder use it
            else:
                self.fpath = os.path.join(os.path.dirname(__file__), "Themes", filename)
                self.folderpath=os.path.join(os.path.dirname(__file__), "Themes")

            if self.fpath:
                download.setPath(self.fpath)
                download.accept()
                download.finished.connect(self.unzipper)

    def unzipper(self):

        print(self.fpath)
        print(self.folderpath)

        with zipfile.ZipFile(self.fpath, 'r') as zip_ref:
            zip_ref.extractall(self.folderpath)
        os.remove(self.fpath)
        w.loadfiles()

        w.themelist.setCurrentRow(len(w.themes)-1) #sets the downloaded item as selected
        w.activateWindow() #brings main window up
        w.themelist.setFocus() #sets focus to make it blue not grey 


        #HIGHLIGHT ADDED THEME IN THE LIST

    def __init__(self, parent=None):
        super(ThemeBrowser, self).__init__(parent)
        self.setAttribute(Qt.WA_QuitOnClose, False) #closes browses when main window is closed because I can't seem to figure out parent-child relations
        self.setWindowTitle("Github Theme Collection")
        self.resize(1300, 600)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.folderpath=w.paththemes
        layout = QVBoxLayout()
        nav=QFrame()
        navlayout=QHBoxLayout()
        
        
        self.url="https://firefoxcss-store.github.io/"
        
        self.web = QWebEngineView()
        self.web.page().profile().downloadRequested.connect(self.downloadRequested)
        self.web.load(QUrl(self.url))

        layout.addWidget(nav)
        layout.addWidget(self.web,1)
        
        back=QPushButton("Back")
        back.clicked.connect(lambda: self.web.page().triggerAction(QWebEnginePage.Back))
        front=QPushButton("Front")
        front.clicked.connect(lambda: self.web.page().triggerAction(QWebEnginePage.Forward))
        
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)


        navlayout.addWidget(back,0)
        navlayout.addWidget(front,0)
        navlayout.addStretch(1)

        self.setLayout(layout)
        nav.setLayout(navlayout)
        

if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec_())
