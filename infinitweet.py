#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui
from utils import *
from PyQt4.QtWebKit import *
from PyQt4.QtCore import *
from bs4 import BeautifulSoup as bs

class MyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)
        self.resize(800, 600)
        self.browser = Browser(self)

class Browser(QWebView):

    def __init__(self,parent=None):
        super(Browser,self).__init__(parent)
        self.auth_done=False
        self.auth,auth_url = auth_step1()
        self.loadFinished.connect(self._result_available)
        self.load(QUrl(auth_url))       

    def _result_available(self, ok):
        if not self.auth_done:
            frame = self.page().mainFrame()
            html= unicode(frame.toHtml()).encode('utf-8')
            soup=bs(html,'lxml')
            elem=soup.find('code')
            if elem:
                pincode = elem.text
                twitter = auth_step2(self.auth,pincode)
                self.auth_done=True
                self.parent().close()

    
    # def load_userdata(self,twitter):
    #     html = json2html.convert(json = twitter.verify_credentials())
    #     self.setHtml(html)



class MyWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.textbox=QtGui.QTextEdit(self)
        self.count_display = QtGui.QLabel(self)
        self.count_display.setAlignment(Qt.AlignCenter)
        self.textbox.textChanged.connect(self.update_char_count) 
        self.tweetbutton=QtGui.QPushButton('Tweet!',self)
        self.tweetbutton.clicked.connect(self.send_tweet)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.textbox)
        self.layout.addWidget(self.count_display)
        self.layout.addWidget(self.tweetbutton)
        self.browser=MyDialog(self)
        self.twitter=check_stored_tokens()
        if not self.twitter:
            self.browser.exec_()
            self.twitter=check_stored_tokens() 


    @QtCore.pyqtSlot()
    def send_tweet(self):
        text= self.textbox.toPlainText()
        if len(text)<140:
            r=self.twitter.update_status(status=text)
        else:
            fn=imagify(text)
            media=self.twitter.media_upload(fn)
            r=self.twitter.update_status(media_ids=[media.media_id_string])
        print r
        self.textbox.clear()

    @QtCore.pyqtSlot()
    def update_char_count(self):
        self.count_display.setNum(len(self.textbox.toPlainText()))



if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(['Infinitweet'])
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    app.setApplicationName('Infinitweet')

    main = MyWindow()
    main.resize(width/4,height/3)
    main.show()

    sys.exit(app.exec_())