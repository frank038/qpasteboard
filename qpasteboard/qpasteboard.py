#!/usr/bin/env python3

# V. 0.9

from cfg import *
import os
import sys
import shutil
from pathlib import Path
from time import time

from PyQt5.QtCore import (Qt, QSize)
from PyQt5.QtGui import (QClipboard, QIcon, QPixmap, QImage)
from PyQt5.QtWidgets import (QApplication, qApp, QStyleFactory, QWidget, QDesktopWidget, QBoxLayout, QAction, QMessageBox, QPushButton, QMenu, QScrollArea, QDialog, QListWidget, QListWidgetItem, QSizePolicy, QTabWidget, QSystemTrayIcon, QHBoxLayout, QVBoxLayout,QLabel)

class firstMessage(QWidget):
    
    def __init__(self, *args):
        super().__init__()
        title = args[0]
        message = args[1]
        self.setWindowTitle(title)
        # self.setWindowIcon(QIcon("icons/file-manager-red.svg"))
        box = QBoxLayout(QBoxLayout.TopToBottom)
        box.setContentsMargins(5,5,5,5)
        self.setLayout(box)
        label = QLabel(message)
        box.addWidget(label)
        button = QPushButton("Close")
        box.addWidget(button)
        button.clicked.connect(self.close)
        self.show()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

STORE_IMAGES = STORE_IMAGES

ccdir = os.getcwd()
clips_path = os.path.join(ccdir, "clips")
images_path = os.path.join(ccdir, "images")

def cr_clips_images():
    if Path(clips_path).exists() == False:
        try:
            os.mkdir(clips_path)
        except Exception as E:
            app = QApplication(sys.argv)
            fm = firstMessage("Error", str(E)+"\n\n    Exiting...")
            sys.exit(app.exec_())
    #
    if Path(images_path).exists() == False:
        try:
            os.mkdir(images_path)
        except Exception as E:
            app = QApplication(sys.argv)
            fm = firstMessage("Error", str(E)+"\n\n    Exiting...")
            sys.exit(app.exec_())
cr_clips_images()

WINW = 600
WINH = 600

try:
    ffile = open(os.path.join(ccdir, "progsize.cfg"), "r")
    WINW, WINH = ffile.readline().split(";")
    WINW = int(WINW)
    WINH = int(WINH)
    ffile.close()
except:
    WINW = 600
    WINH = 600


DWINW = 400
DWINH = 400
try:
    ffile = open(os.path.join(ccdir, "previewsize.cfg"), "r")
    DWINW, DWINH = ffile.readline().split(";")
    DWINW = int(DWINW)
    DWINH = int(DWINH)
    ffile.close()
except:
    DWINW = 400
    DWINH = 400

dialWidth = 500

# store each preview
CLIPS_DICT = {}

### clips
clips_temp = os.listdir(clips_path)

for iitem in sorted(clips_temp, reverse=False):
    iitem_text = ""
    try:
        tfile = open(os.path.join(clips_path, iitem), "r")
        iitem_text = tfile.read()
        tfile.close()
    except Exception as E:
        app = QApplication(sys.argv)
        fm = firstMessage("Error", str(E)+"\n\n    Exiting...")
        sys.exit(app.exec_())
    #
    if len(iitem_text) > int(CHAR_PREVIEW):
        text_prev = iitem_text[0:int(CHAR_PREVIEW)]+" [...]"
        CLIPS_DICT[iitem] = [text_prev]
    else:
        CLIPS_DICT[iitem] = [iitem_text]


class Qclip:
    def __init__(self):
        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        #
        self.app.clipboard().changed.connect(self.clipboardChanged)
        #
        # set new style globally
        if WIDGET_THEME:
            wtheme = QStyleFactory.create(WIDGET_THEME)
            self.app.setStyle(wtheme)
        #
        if TRAY_ICON_THEME == 1:
            icon = QIcon("icons/qpasteboard2.png")
        else:
            icon = QIcon("icons/qpasteboard.png")
        #
        self.stop_tracking = 0
        #
        self.menu = QMenu()
        #
        self.settingAction = self.menu.addAction("Stop tracking")
        self.settingAction.triggered.connect(self.stoptracking)
        #
        if STORE_IMAGES:
            self.imageAction = self.menu.addAction("Store images")
        else:
            self.imageAction = self.menu.addAction("Store images (stopped)")
        self.imageAction.triggered.connect(self.storeImages)
        #
        exitAction = self.menu.addAction("exit")
        exitAction.triggered.connect(qApp.quit)
        #
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setContextMenu(self.menu)
        self.tray.show()
        self.tray.setToolTip("Qpasteboard")
        #
        self.tray.activated.connect(self.mainWidget)
        # the first clip stored
        self.actual_clip = None
        #
        self.item_text_num = 0
        self.item_image_num = 0
        
        
    def clipboardChanged(self, mode):
        #
        if mode == 0 and not self.stop_tracking:
            if SKIP_FILES:
                if self.app.clipboard().mimeData().hasFormat("x-special/gnome-copied-files"):
                    return
            #
            if self.app.clipboard().mimeData().hasFormat("text/plain"):
                text = self.app.clipboard().text()
                # skip if too large
                if len(text) > CLIP_MAX_SIZE:
                    return
                #
                if text and text != self.actual_clip:
                    idx = time_now = str(int(time()))
                    i = 0
                    while os.path.exists(os.path.join(clips_path, time_now)):
                        sleep(0.1)
                        time_now = str(int(time()))
                        i += 1
                        if i == 10:
                            break
                        return
                    #
                    try:
                        ff = open(os.path.join(clips_path, idx), "w")
                        ff.write(text)
                        ff.close()
                    except Exception as E:
                        MyDialog("Error", str(E), None)
                        return
                    #
                    if len(text) > int(CHAR_PREVIEW):
                        text_prev = text[0:int(CHAR_PREVIEW)]+" [...]"
                        CLIPS_DICT[str(idx)] = [text_prev]
                    else:
                        CLIPS_DICT[str(idx)] = [text]
                    # remove older entries
                    if HISTORY_SIZE:
                        list_clips = sorted(os.listdir(clips_path), reverse=True)
                        num_clips = len(list_clips)
                        #
                        if num_clips > int(HISTORY_SIZE):
                            iitem = list_clips[-1]
                            try:
                                os.remove(os.path.join(clips_path, iitem))
                            except Exception as E:
                                MyDialog("Error", str(E), None)
                                return

            elif self.app.clipboard().mimeData().hasFormat("image/png"):
                if STORE_IMAGES:
                    image = self.app.clipboard().image()
                    if image.isNull():
                        return
                    #
                    idx = time_now = str(int(time()))
                    i = 0
                    while os.path.exists(os.path.join(clips_path, time_now)):
                        sleep(0.1)
                        time_now = str(int(time()))
                        i += 1
                        if i == 10:
                            break
                        return
                    #
                    try:
                        image.save(os.path.join(images_path, idx), IMAGE_FORMAT)
                    except Exception as E:
                        MyDialog("Error", str(E), None)
        
    def stoptracking(self, action):
        if self.stop_tracking:
            self.settingAction.setText("Stop tracking")
            if TRAY_ICON_THEME == 1:
                icon = QIcon("icons/qpasteboard2.png")
            else:
                icon = QIcon("icons/qpasteboard.png")
            self.stop_tracking = 0
        else:
            self.settingAction.setText("Start tracking")
            if TRAY_ICON_THEME == 1:
                icon = QIcon("icons/qpasteboard-stop2.png")
            else:
                icon = QIcon("icons/qpasteboard-stop.png")
            self.stop_tracking = 1
        #
        self.tray.setIcon(icon)
    
    def storeImages(self, mode):
        global STORE_IMAGES
        STORE_IMAGES = not STORE_IMAGES
        if STORE_IMAGES:
            self.imageAction.setText("Store images")
        else:
            self.imageAction.setText("Store images (stopped)")
        
    def mainWidget(self):
        self.item_text_num = 0
        self.item_image_num = 0
        #
        self.cwindow = QWidget()
        self.cwindow.setWindowIcon(QIcon("icons/clipman.svg"))
        self.cwindow.setContentsMargins(0,0,0,0)
        self.cwindow.resize(WINW, WINH)
        #
        self.mainBox = QHBoxLayout()
        self.mainBox.setContentsMargins(2,2,2,2)
        self.cwindow.setLayout(self.mainBox)
        ####### left
        self.leftBox = QVBoxLayout()
        self.mainBox.addLayout(self.leftBox)
        #
        self.historyLBL = QLabel()
        self.on_label_text(self.historyLBL, 0, "in history")
        self.leftBox.addWidget(self.historyLBL)
        #
        if STORE_IMAGES:
            self.imageLBL = QLabel()
            self.on_label_text(self.imageLBL, 0, "images")
            self.leftBox.addWidget(self.imageLBL)
        #
        self.clearBTN = QPushButton("Empty history")
        self.clearBTN.clicked.connect(self.on_clear_history)
        self.leftBox.addWidget(self.clearBTN)
        #
        self.leftBox.addStretch()
        #
        self.closeBTN = QPushButton("Close")
        self.closeBTN.clicked.connect(self.on_close)
        self.leftBox.addWidget(self.closeBTN)
        ####### right
        self.ctab = QTabWidget()
        self.ctab.setMovable(False)
        self.mainBox.addWidget(self.ctab)
        self.ctab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #
        self.textLW = QListWidget()
        self.textLW.setSelectionMode(1)
        self.textLW.itemClicked.connect(self.on_item_clicked)
        self.ctab.addTab(self.textLW, "Text")
        ####
        # texts
        list_items = sorted(CLIPS_DICT, reverse=True)
        #
        for iitem in list_items:
            iitem_text = CLIPS_DICT[iitem][0]
            self.on_add_item(iitem_text, iitem)
        #
        self.on_label_text(self.historyLBL, self.item_text_num, "in history")
        # images
        if STORE_IMAGES:
            image_temp = os.listdir(images_path)
            if image_temp:
                for iimage in image_temp:
                    iwidget = QWidget()
                    ilayout = QVBoxLayout()
                    ilayout.setContentsMargins(2,2,2,2)
                    btn_layout = QHBoxLayout()
                    btn_layout.setContentsMargins(0,0,0,0)
                    iwidget.setLayout(ilayout)
                    #
                    image_scroll = QScrollArea()
                    image_scroll.setWidgetResizable(True)
                    pimage = QPixmap(os.path.join(images_path, iimage))
                    limage = QLabel()
                    limage.setPixmap(pimage)
                    image_scroll.setWidget(limage)
                    ilayout.addWidget(image_scroll)
                    #
                    apply_btn = QPushButton()
                    apply_btn.setIcon(QIcon("icons/apply.png"))
                    apply_btn.setToolTip("Copy this image")
                    apply_btn.clicked.connect(self.on_apply_image)
                    btn_layout.addWidget(apply_btn)
                    #
                    save_btn = QPushButton()
                    save_btn.setIcon(QIcon("icons/save.png"))
                    save_btn.setToolTip("Save this image")
                    save_btn.clicked.connect(self.on_save_image)
                    btn_layout.addWidget(save_btn)
                    #
                    delete_btn = QPushButton()
                    delete_btn.setIcon(QIcon("icons/remove.png"))
                    delete_btn.setToolTip("Delete this image")
                    delete_btn.clicked.connect(self.on_delete_image)
                    btn_layout.addWidget(delete_btn)
                    #
                    ilayout.addLayout(btn_layout)
                    #
                    iwidget.iimage = iimage
                    iwidget.pimage = pimage
                    self.ctab.insertTab(1, iwidget, "Image")
                    #
                    self.item_image_num += 1
            #
            if self.item_image_num == 1:
                self.on_label_text(self.imageLBL, self.item_image_num, "image")
            else:
                self.on_label_text(self.imageLBL, self.item_image_num, "images")
        #
        self.cwindow.show()
        
    def on_apply_image(self):
        try:
            curr_idx = self.ctab.currentIndex()
            pimage = self.ctab.widget(curr_idx).pimage
            self.app.clipboard().setPixmap(pimage)
        except Exception as E:
            MyDialog("Error", str(E), self.cwindow)
    
    def on_save_image(self):
        try:
            curr_idx = self.ctab.currentIndex()
            iimage = self.ctab.widget(curr_idx).iimage
            iname = "Image_"+str(int(time()))
            shutil.copy(os.path.join(images_path, iimage), os.path.join( os.path.expanduser("~"), iname ) )
            MyDialog("Info", "\n{}\nsaved in your home folder.".format(iname), self.cwindow)
        except Exception as E:
            MyDialog("Error", str(E), self.cwindow)
    
    def on_delete_image(self):
        try:
            curr_idx = self.ctab.currentIndex()
            twidget = self.ctab.widget(curr_idx)
            os.remove(os.path.join(images_path, twidget.iimage))
            self.ctab.removeTab(curr_idx)
            twidget.deleteLater()
            self.item_image_num -= 1
            if self.item_image_num == 1:
                self.on_label_text(self.imageLBL, self.item_image_num, "image")
            else:
                self.on_label_text(self.imageLBL, self.item_image_num, "images")
        except Exception as E:
            MyDialog("Error", str(E), self.cwindow)
    
    def on_label_text(self, lbl, num, text):
        lbl.setText("<b>{}</b> {}".format(num, text))
        lbl.setAlignment(Qt.AlignCenter)
    
    #
    def on_add_item(self, text, idx):
        lw = QListWidgetItem()
        widgetItem = QWidget()
        widgetTXT =  QLabel(text=text)
        #
        previewBTN = QPushButton()
        previewBTN.setIcon(QIcon("icons/preview.png"))
        previewBTN.clicked.connect(lambda:self.on_preview(idx))
        previewBTN.setToolTip("Preview")
        #
        removeBTN = QPushButton()
        removeBTN.setIcon(QIcon("icons/list-remove.png"))
        removeBTN.clicked.connect(lambda:self.on_delete_item(idx))
        removeBTN.setToolTip("Delete this item")
        #
        widgetItemL = QHBoxLayout()
        widgetItemL.addWidget(widgetTXT)
        widgetItemL.addStretch()
        widgetItemL.addWidget(previewBTN)
        widgetItemL.addWidget(removeBTN)
        #
        widgetItem.setLayout(widgetItemL)  
        lw.setSizeHint(widgetItem.sizeHint())
        #
        lw.idx = idx
        #
        self.textLW.addItem(lw)
        self.textLW.setItemWidget(lw, widgetItem)
        #
        self.item_text_num += 1
        
    def on_item_clicked(self, iitem):
        clip_text = ""
        ff = open(os.path.join(clips_path, iitem.idx), "r")
        clip_text = ff.read()
        ff.close()
        # 
        if clip_text == self.actual_clip:
            self.app.clipboard().setText(clip_text)
        else:
            # remove the clip file
            try:
                os.remove(os.path.join(clips_path, str(iitem.idx)))
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
                return
            self.actual_clip = clip_text
            self.textLW.takeItem(self.textLW.row(iitem))
            del CLIPS_DICT[iitem.idx]
            del iitem
            self.app.clipboard().setText(clip_text)
            ####
            idx = time_now = str(int(time()))
            i = 0
            while os.path.exists(os.path.join(clips_path, time_now)):
                sleep(0.1)
                time_now = str(int(time()))
                i += 1
                if i == 10:
                    break
                return
            #
            try:
                ff = open(os.path.join(clips_path, idx), "w")
                ff.write(clip_text)
                ff.close()
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
                return
            #
            if len(clip_text) > int(CHAR_PREVIEW):
                text_prev = clip_text[0:int(CHAR_PREVIEW)]+" [...]"
                CLIPS_DICT[str(idx)] = [text_prev]
            else:
                CLIPS_DICT[str(idx)] = [clip_text]
            ####
        self.cwindow.close()
        
    
    def on_close_preview(self):
        new_w = self.dialog.size().width()
        new_h = self.dialog.size().height()
        global DWINW
        global DWINH
        if new_w != DWINW or new_h != DWINH:
            try:
                with open(os.path.join(ccdir, "previewsize.cfg"), "w") as ff:
                    ff.write("{};{}".format(new_w, new_h))
                #
                DWINW = new_w
                DWINH = new_h
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
        self.dialog.close()
        
    
    def on_preview(self, idx):
        self.dialog = QDialog()
        self.dialog.resize(int(DWINW), int(DWINH))
        self.dialog.setContentsMargins(0,0,0,0)
        self.dialog.setWindowTitle("Preview")
        self.dialog.setWindowIcon(QIcon("icons/clipman.svg"))
        self.dialog.setModal(True)
        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        self.dialog.setLayout(layout)
        #
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        layout.addWidget(scrollArea)
        
        textW = QLabel()
        scrollArea.setWidget(textW)
        textW.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text = ""
        with open(os.path.join(clips_path, idx), "r") as ff:
            text = ff.read()
        textW.setText(text)
        textW.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #
        closeDBTN = QPushButton("Close")
        closeDBTN.clicked.connect(self.on_close_preview)
        layout.addWidget(closeDBTN)
        #
        self.dialog.show()
    
    # text
    def on_delete_item(self, idx):
        num_items = self.textLW.count()
        itemW = None
        #
        for i in range(num_items):
            if self.textLW.item(i).idx == idx:
                itemW = self.textLW.item(i)
                break
        if itemW:
            # remove the file
            try:
                os.remove(os.path.join(clips_path, str(itemW.idx)))
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
                return
            #
            del CLIPS_DICT[str(itemW.idx)]
            self.textLW.takeItem(self.textLW.row(itemW))
            del itemW
            #
            self.item_text_num -= 1
            self.on_label_text(self.historyLBL, self.item_text_num, "in history")
    
    def on_clear_history(self):
        ret = MyDialog("Question", "Remove all the items?", self.cwindow)
        if ret.retval == QMessageBox.Yes:
            global CLIPS_DICT
            try:
                clips_temp = os.listdir(clips_path)
                if clips_temp:
                    for iitem in clips_temp:
                        os.remove(os.path.join(clips_path, iitem))
                        del CLIPS_DICT[iitem]
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
            try:
                #
                images_temp = os.listdir(images_path)
                if images_temp:
                    for iitem in images_temp:
                        os.remove(os.path.join(images_path, iitem))
            except Exception as E:
                MyDialog("Error", str(E), self.cwindow)
            #
            self.textLW.clear()
            #
            self.cwindow.close()
    
    def on_close(self):
        new_w = self.cwindow.size().width()
        new_h = self.cwindow.size().height()
        global WINW
        global WINH
        #
        if new_w != int(WINW) or new_h != int(WINH):
            try:
                ifile = open("progsize.cfg", "w")
                ifile.write("{};{}".format(new_w, new_h))
                ifile.close()
                WINW = new_w
                WINH = new_h
            except:
                pass
        #
        self.cwindow.close()
    
    def run(self):
        self.app.exec_()
        sys.exit()


# type - message - parent
class MyDialog(QMessageBox):
    def __init__(self, *args):
        super(MyDialog, self).__init__(args[-1])
        if args[0] == "Info":
            self.setIcon(QMessageBox.Information)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Error":
            self.setIcon(QMessageBox.Critical)
            self.setStandardButtons(QMessageBox.Ok)
        elif args[0] == "Question":
            self.setIcon(QMessageBox.Question)
            self.setStandardButtons(QMessageBox.Yes|QMessageBox.Cancel)
        self.setWindowIcon(QIcon("icons/clipman.svg"))
        self.setWindowTitle(args[0])
        self.resize(dialWidth,100)
        self.setText(args[1])
        self.retval = self.exec_()
    
    def event(self, e):
        result = QMessageBox.event(self, e)
        #
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 
        return result

if __name__ == "__main__":
    app = Qclip()
    app.run()
