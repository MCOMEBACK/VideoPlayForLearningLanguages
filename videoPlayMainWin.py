from fileinput import filename
from PyQt6.QtWidgets import QMainWindow,QApplication,QFileDialog
import sys
from MainWindow import Ui_MainWindow
from PyQt6.QtMultimedia import QMediaPlayer,QAudioOutput
from PyQt6.QtCore import QDir,QUrl,Qt,QFileInfo,QEvent
from PyQt6.QtGui import QIcon
import os 
import os.path 

from datetime import datetime

text_srt=[]
index_srt=0
loaded=True
def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fff':
            return True
    return False
class VideoPlay(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("视频播放器")

        self.player = QMediaPlayer(self)
        self.audioOutput = QAudioOutput()

        self.player.setVideoOutput(self.ui.videoWidget)
        self.ui.videoWidget.installEventFilter(self)

        self.__duration = ""
        self.__duration_ =0
        self.__curPos = ""
        self._count_text=0
        self._slider_move=False
        self.subtitles_=False
        self.click_checkBOX=0
        
        self.result_translate_list=[]
        self.player.playbackStateChanged.connect(self.do_stateChanged)
        self.player.positionChanged.connect(self.do_positionChanged)
        self.player.durationChanged.connect(self.do_durationChanged)
     
        self.ui.checkBox.setChecked(True)

    def closeEvent(self, event):
        if (self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState):
            self.player.stop()

    def eventFilter(self, watched, event):
        if (watched != self.ui.videoWidget):
            return super().eventFilter(watched,event)
        
        if (event.type() == QEvent.Type.MouseButtonPress):
            if (event.button() == Qt.MouseButton.LeftButton):
                if (self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState):
                    self.player.pause()
                else:
                    self.player.play()

        if (event.type() == QEvent.Type.KeyPress):
            if (event.key() == Qt.Key.Key_Escape):
                if (self.ui.videoWidget.isFullScreen()):
                    self.ui.videoWidget.setFullScreen(False)
        return super().eventFilter(watched,event)


    def on_btnOpen_pressed(self):
        
        curPath = QDir.currentPath()
        title = "选择视频文件"
        filt = "视频文件(*.wmv *avi *.mp4 *.mov);;所有文件(*.*)"
        fileName,flt = QFileDialog.getOpenFileName(self,title,curPath,filt)
        if fileName == "":
            return
       
        fileInfo = QFileInfo(fileName)
        baseName = fileInfo.fileName()#视频的名字
        filePath = fileInfo.path()
        self.ui.LabCurMedia.setText(baseName)
        #print(filePath) 


        dir = filePath #读取字幕
        num_subtitles_=0
        files = os.listdir(dir) 
        for filename_srt in files:
          
          if os.path.splitext(filename_srt)[1] == '.srt':
           
           if filename_srt[0] == baseName[0] :
            filePath_srt=filePath+"/"+filename_srt
            #print(filePath_srt) 
            subtitles = []
            num_subtitles_=num_subtitles_+1
            print(num_subtitles_)
            with open(filePath_srt, encoding='utf-8-sig') as srt_file:
                lines = srt_file.readlines()
                num_lines = len(lines)
                
                i = 0
                while i < num_lines:
                    #print(lines[i].strip().isdigit())
                    if lines[i].strip().isdigit():
                        
                        index = int(lines[i].strip())
                        #print(lines[i].strip())
                        #print(i)
                        i += 1
                        #print(lines[i].strip())
                        time_range = lines[i].strip().split(' --> ')
                        start_time = time_range[0]
                        end_time = time_range[1]
                        #time_string=text_srt[index_srt].get('start_time')
                        time_format = "%H:%M:%S,%f"
                        time_obj = datetime.strptime(start_time, time_format)
                        start_time = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second) * 1000 + time_obj.microsecond / 1000
                        #print(start_time_seconds)

                        #time_string=text_srt[index_srt].get('end_time')
                        time_format = "%H:%M:%S,%f"
                        time_obj = datetime.strptime(end_time, time_format)
                        end_time = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second) * 1000 + time_obj.microsecond / 1000

                        i += 1
                        text = []
                        text_cn=[]
                        
                        while i < num_lines and lines[i].strip() != '':

                            if is_contains_chinese(num_lines and lines[i].strip()):
                                text_cn.append(lines[i].strip())

                            else:
                                text.append(lines[i].strip())
                            i += 1
                            

                        text = ' '.join(text)
                        text_cn = ' '.join(text_cn)
                        subtitle = {
                            'index': index,
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': text,
                            'text_cn': text_cn
                        }
                        subtitles.append(subtitle)
                    else:
                        i += 1
        
        global text_srt
        if num_subtitles_>0:
          text_srt=subtitles
          self.subtitles_=True
          #print(self.subtitles_)
          self._count_text=len([item for item in text_srt if isinstance(item, dict)])
        else:
           self.subtitles_=False
           #print(self.subtitles_)
        #print(self._count_text)#打印字典个数
        #print(text_srt[0].get('start_time'))
        '''for subtitle in subtitles:
            #print('Subtitle index:', subtitle['index'])
            #print('Subtitle start time:', subtitle['start_time'])
            #print('Subtitle end time:', subtitle['end_time'])
            #print('Subtitle end time:', subtitle['text'][0])
            #self.result_translate_list.append(subtitle['text'][0])
            result_translate = translator.translate(subtitle['text'][0], src='ru', dest='zh-cn')
            print(result_translate.text) 
            self.result_translate_list.append(result_translate.text)
        print(self.result_translate_list)    '''
        media = QUrl.fromLocalFile(fileName)
        self.player.setAudioOutput(self.audioOutput)
        self.player.setSource(media)
        self.player.play()
    
    def on_btnFullScreen_pressed(self):
        self.ui.videoWidget.setFullScreen(True)

    def on_btnPlay_pressed(self):
        self.player.play()
    
    def on_btnPause_pressed(self):
        self.player.pause()



    
    def on_btnStop_pressed(self):
        if self.subtitles_==True:
            global index_srt
            global loaded
            index_srt=0
            self.ui.textEdit_1.setText("")
            self.ui.textEdit_2.setText("")
            self.ui.textEdit_3.setText("")
            self.ui.textEdit_4.setText("")
            self.ui.textEdit_5.setText("")
            self.ui.textEdit_6.setText("")
            self.ui.textEdit_7.setText("")
            self.ui.textEdit_8.setText("")
            loaded=True
        else:
            _str_='无字幕'
            self.ui.textEdit_1.setText("")
            self.ui.textEdit_2.setText("")
            self.ui.textEdit_3.setText("")
            self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+_str_+'</font>')
            self.ui.textEdit_5.setText("")
            self.ui.textEdit_6.setText("")
            self.ui.textEdit_7.setText("")
            self.ui.textEdit_8.setText("")           
        self.player.stop()

    def do_stateChanged(self,state):
        if (state == QMediaPlayer.PlaybackState.PlayingState):
            isPlaying = True
        else:
            isPlaying = False
        self.ui.btnPlay.setEnabled(not isPlaying)
        self.ui.btnPause.setEnabled(isPlaying)
        self.ui.btnStop.setEnabled(isPlaying)

    def do_durationChanged(self,duration):
        self.ui.sliderPosition.setMaximum(duration)
        self.__duration_=duration
        secs = duration/1000
        mins = secs/60
        secs = secs%60
        self.__duration = "%d:%d"%(mins,secs)
        self.ui.LabRatio.setText(self.__curPos+"/"+self.__duration)


        
    def do_positionChanged(self,position):
        
        #print(check_box_status)
        if (self.ui.sliderPosition.isSliderDown()):#如果正在拖动滑条，退出
            self._slider_move=True
            return
        #print(position)
        self.ui.sliderPosition.setSliderPosition(position)
        secs = position/1000
        mins = secs/60
        secs = secs%60
        self.__curPos = "%d:%d"%(mins,secs)
        self.ui.LabRatio.setText(self.__curPos+"/"+self.__duration)
        global loaded
        global index_srt
        '''time_string=text_srt[index_srt].get('start_time')
        time_format = "%H:%M:%S,%f"
        time_obj = datetime.strptime(time_string, time_format)
        start_time_seconds = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second) * 1000 + time_obj.microsecond / 1000
        #print(start_time_seconds)

        time_string=text_srt[index_srt].get('end_time')
        time_format = "%H:%M:%S,%f"
        time_obj = datetime.strptime(time_string, time_format)
        end_time_seconds = (time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second) * 1000 + time_obj.microsecond / 1000'''
        #print(text_srt[index_srt].get('end_time'))
        #print(index_srt)
        #print(self.ui.checkBox.isChecked())
        if self.subtitles_==True:
          if loaded:
           if text_srt[index_srt].get('start_time')<position:
            if text_srt[index_srt].get('end_time')>position:
             #print(text_srt[index_srt].get('text'))
             #print(self._count_text)
             #print(index_srt)
             a=int(self._count_text-index_srt)
             #print(a)
             if self.ui.checkBox.isChecked():
                #print(self.ui.checkBox.isChecked())
                if index_srt==0:
                    '''self.ui.textEdit_1.setToolTip(text_srt[index_srt-3].get('text_cn'))
                    self.ui.textEdit_2.setToolTip(text_srt[index_srt-2].get('text_cn'))
                    self.ui.textEdit_3.setToolTip(text_srt[index_srt-1].get('text_cn'))'''
                    self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                    self.ui.textEdit_5.setToolTip(text_srt[index_srt+1].get('text_cn'))
                    self.ui.textEdit_6.setToolTip(text_srt[index_srt+2].get('text_cn'))
                    self.ui.textEdit_7.setToolTip(text_srt[index_srt+3].get('text_cn'))
                    self.ui.textEdit_8.setToolTip(text_srt[index_srt+4].get('text_cn'))
                
                    self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                    str_=text_srt[index_srt].get('text')
                    self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+str_+'</font>')
                    self.ui.textEdit_5.setText(text_srt[index_srt+1].get('text'))
                    self.ui.textEdit_6.setText(text_srt[index_srt+2].get('text'))
                    self.ui.textEdit_7.setText(text_srt[index_srt+3].get('text'))
                    self.ui.textEdit_8.setText(text_srt[index_srt+4].get('text'))
                if index_srt==1:
                    #self.ui.textEdit_1.setToolTip(text_srt[index_srt-3].get('text_cn'))
                    #self.ui.textEdit_2.setToolTip(text_srt[index_srt-2].get('text_cn'))
                    self.ui.textEdit_3.setToolTip(text_srt[index_srt-1].get('text_cn'))
                    self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                    self.ui.textEdit_5.setToolTip(text_srt[index_srt+1].get('text_cn'))
                    self.ui.textEdit_6.setToolTip(text_srt[index_srt+2].get('text_cn'))
                    self.ui.textEdit_7.setToolTip(text_srt[index_srt+3].get('text_cn'))
                    self.ui.textEdit_8.setToolTip(text_srt[index_srt+4].get('text_cn'))

                    self.ui.textEdit_3.setText(text_srt[index_srt-1].get('text')) 
                    #self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                    str_=text_srt[index_srt].get('text')
                    self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+str_+'</font>')
                    self.ui.textEdit_5.setText(text_srt[index_srt+1].get('text'))
                    self.ui.textEdit_6.setText(text_srt[index_srt+2].get('text'))
                    self.ui.textEdit_7.setText(text_srt[index_srt+3].get('text'))
                    self.ui.textEdit_8.setText(text_srt[index_srt+4].get('text')[0])
                if index_srt==2:
                    #self.ui.textEdit_1.setToolTip(text_srt[index_srt-3].get('text_cn'))
                    self.ui.textEdit_2.setToolTip(text_srt[index_srt-2].get('text_cn'))
                    self.ui.textEdit_3.setToolTip(text_srt[index_srt-1].get('text_cn'))
                    self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                    self.ui.textEdit_5.setToolTip(text_srt[index_srt+1].get('text_cn'))
                    self.ui.textEdit_6.setToolTip(text_srt[index_srt+2].get('text_cn'))
                    self.ui.textEdit_7.setToolTip(text_srt[index_srt+3].get('text_cn'))
                    self.ui.textEdit_8.setToolTip(text_srt[index_srt+4].get('text_cn'))

                    self.ui.textEdit_2.setText(text_srt[index_srt-2].get('text'))
                    self.ui.textEdit_3.setText(text_srt[index_srt-1].get('text'))
                    #self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn')) 
                    str_=text_srt[index_srt].get('text')
                    self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+str_+'</font>')
                    self.ui.textEdit_5.setText(text_srt[index_srt+1].get('text'))
                    self.ui.textEdit_6.setText(text_srt[index_srt+2].get('text'))
                    self.ui.textEdit_7.setText(text_srt[index_srt+3].get('text'))
                    self.ui.textEdit_8.setText(text_srt[index_srt+4].get('text'))
                if index_srt>=3:
                    if a==4:
                        #print(self._count_text-index_srt)
                        self.ui.textEdit_1.setToolTip(text_srt[index_srt-3].get('text_cn'))
                        self.ui.textEdit_2.setToolTip(text_srt[index_srt-2].get('text_cn'))
                        self.ui.textEdit_3.setToolTip(text_srt[index_srt-1].get('text_cn'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                        self.ui.textEdit_5.setToolTip(text_srt[index_srt+1].get('text_cn'))
                        self.ui.textEdit_6.setToolTip(text_srt[index_srt+2].get('text_cn'))
                        self.ui.textEdit_7.setToolTip(text_srt[index_srt+3].get('text_cn'))
                        #self.ui.textEdit_8.setToolTip(text_srt[index_srt+4].get('text_cn'))

                        self.ui.textEdit_1.setText(text_srt[index_srt-3].get('text'))
                        self.ui.textEdit_2.setText(text_srt[index_srt-2].get('text'))
                        self.ui.textEdit_3.setText(text_srt[index_srt-1].get('text'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                        str_=text_srt[index_srt].get('text')
                        self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+str_+'</font>')
                        self.ui.textEdit_5.setText(text_srt[index_srt+1].get('text'))
                        self.ui.textEdit_6.setText(text_srt[index_srt+2].get('text'))
                        self.ui.textEdit_7.setText(text_srt[index_srt+3].get('text'))
                        self.ui.textEdit_8.setText("")
                    elif a==3:
                        self.ui.textEdit_1.setToolTip(text_srt[index_srt-3].get('text_cn'))
                        self.ui.textEdit_2.setToolTip(text_srt[index_srt-2].get('text_cn'))
                        self.ui.textEdit_3.setToolTip(text_srt[index_srt-1].get('text_cn'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                        self.ui.textEdit_5.setToolTip(text_srt[index_srt+1].get('text_cn'))
                        self.ui.textEdit_6.setToolTip(text_srt[index_srt+2].get('text_cn'))
                        '''self.ui.textEdit_7.setToolTip(text_srt[index_srt+3].get('text_cn'))
                        self.ui.textEdit_8.setToolTip(text_srt[index_srt+4].get('text_cn'))'''
                    
                        self.ui.textEdit_1.setText(text_srt[index_srt-3].get('text'))
                        self.ui.textEdit_2.setText(text_srt[index_srt-2].get('text'))
                        self.ui.textEdit_3.setText(text_srt[index_srt-1].get('text'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn')) 
                        str_=text_srt[index_srt].get('text')
                        self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+str_+'</font>')
                        self.ui.textEdit_5.setText(text_srt[index_srt+1].get('text'))
                        self.ui.textEdit_6.setText(text_srt[index_srt+2].get('text'))
                        self.ui.textEdit_7.setText("")
                        self.ui.textEdit_8.setText("")
                    elif a==2:
                        self.ui.textEdit_1.setToolTip(text_srt[index_srt-3].get('text_cn'))
                        self.ui.textEdit_2.setToolTip(text_srt[index_srt-2].get('text_cn'))
                        self.ui.textEdit_3.setToolTip(text_srt[index_srt-1].get('text_cn'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                        self.ui.textEdit_5.setToolTip(text_srt[index_srt+1].get('text_cn'))
                        '''self.ui.textEdit_6.setToolTip(text_srt[index_srt+2].get('text_cn'))
                        self.ui.textEdit_7.setToolTip(text_srt[index_srt+3].get('text_cn'))
                        self.ui.textEdit_8.setToolTip(text_srt[index_srt+4].get('text_cn'))'''

                        self.ui.textEdit_1.setText(text_srt[index_srt-3].get('text'))
                        self.ui.textEdit_2.setText(text_srt[index_srt-2].get('text'))
                        self.ui.textEdit_3.setText(text_srt[index_srt-1].get('text'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn')) 
                        str_=text_srt[index_srt].get('text')
                        self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+str_+'</font>')
                        self.ui.textEdit_5.setText(text_srt[index_srt+1].get('text'))
                        self.ui.textEdit_6.setText("")
                        self.ui.textEdit_7.setText("")
                        self.ui.textEdit_8.setText("")
                    elif a==1:
                        self.ui.textEdit_1.setToolTip(text_srt[index_srt-3].get('text_cn'))
                        self.ui.textEdit_2.setToolTip(text_srt[index_srt-2].get('text_cn'))
                        self.ui.textEdit_3.setToolTip(text_srt[index_srt-1].get('text_cn'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                        '''self.ui.textEdit_5.setToolTip(text_srt[index_srt+1].get('text_cn'))
                        self.ui.textEdit_6.setToolTip(text_srt[index_srt+2].get('text_cn'))
                        self.ui.textEdit_7.setToolTip(text_srt[index_srt+3].get('text_cn'))
                        self.ui.textEdit_8.setToolTip(text_srt[index_srt+4].get('text_cn'))'''
                        self.ui.textEdit_1.setText(text_srt[index_srt-3].get('text'))
                        self.ui.textEdit_2.setText(text_srt[index_srt-2].get('text'))
                        self.ui.textEdit_3.setText(text_srt[index_srt-1].get('text'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                        str_=text_srt[index_srt].get('text')
                        self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+str_+'</font>') 
                        self.ui.textEdit_5.setText("")
                        self.ui.textEdit_6.setText("")
                        self.ui.textEdit_7.setText("")
                        self.ui.textEdit_8.setText("")
                    else:
                        self.ui.textEdit_1.setToolTip(text_srt[index_srt-3].get('text_cn'))
                        self.ui.textEdit_2.setToolTip(text_srt[index_srt-2].get('text_cn'))
                        self.ui.textEdit_3.setToolTip(text_srt[index_srt-1].get('text_cn'))
                        self.ui.textEdit_4.setToolTip(text_srt[index_srt].get('text_cn'))
                        self.ui.textEdit_5.setToolTip(text_srt[index_srt+1].get('text_cn'))
                        self.ui.textEdit_6.setToolTip(text_srt[index_srt+2].get('text_cn'))
                        self.ui.textEdit_7.setToolTip(text_srt[index_srt+3].get('text_cn'))
                        self.ui.textEdit_8.setToolTip(text_srt[index_srt+4].get('text_cn'))

                        self.ui.textEdit_1.setText(text_srt[index_srt-3].get('text'))
                        self.ui.textEdit_2.setText(text_srt[index_srt-2].get('text'))
                        self.ui.textEdit_3.setText(text_srt[index_srt-1].get('text')) 
                        #result = self.translator.translate(text_srt[index_srt].get('text')[0], src='ru', dest='zh-cn')
                        str_=text_srt[index_srt].get('text')
                        self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+str_+'</font>')
                        self.ui.textEdit_5.setText(text_srt[index_srt+1].get('text'))
                        self.ui.textEdit_6.setText(text_srt[index_srt+2].get('text'))
                        self.ui.textEdit_7.setText(text_srt[index_srt+3].get('text'))
                        self.ui.textEdit_8.setText(text_srt[index_srt+4].get('text'))
             else:
                    self.ui.textEdit_1.setText("")
                    #print(self.ui.checkBox.isChecked())
                    self.ui.textEdit_2.setText("")
                    self.ui.textEdit_3.setText("")
                    self.ui.textEdit_4.setText("")
                    self.ui.textEdit_5.setText("")
                    self.ui.textEdit_6.setText("")
                    self.ui.textEdit_7.setText("")
                    self.ui.textEdit_8.setText("")


            loaded=False #判断字幕是否已经被加载，如果已经被加载就不进行更新
        else:
            _str_='    无字幕'
            self.ui.textEdit_1.setText("")
            self.ui.textEdit_2.setText("")
            self.ui.textEdit_3.setText("")
            self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+_str_+'</font>')
            self.ui.textEdit_5.setText("")
            self.ui.textEdit_6.setText("")
            self.ui.textEdit_7.setText("")
            self.ui.textEdit_8.setText("")
             
        if self._slider_move:
            
            self._slider_move=False
        else:
            if self.subtitles_==True:
             if not self.ui.checkBox.isChecked():
              self.ui.textEdit_1.setText("")
              self.ui.textEdit_2.setText("")
              self.ui.textEdit_3.setText("")
              self.ui.textEdit_4.setText("")
              self.ui.textEdit_5.setText("")
              self.ui.textEdit_6.setText("")
              self.ui.textEdit_7.setText("")
              self.ui.textEdit_8.setText("") 
              self.click_checkBOX=1#此时字幕处于关闭状态            
             if position>text_srt[index_srt].get('end_time'):

                #index_srt=index_srt+1 #问题：往回滑动进度条字幕不更新
                #print(index_srt)
                result = max([item["end_time"] for item in text_srt if item["end_time"] < position], default=None)
                #print(result)
                max_index = next(i for i, v in enumerate(text_srt) if v["end_time"] == result)
                #print(max_index)
                index_srt=max_index+1

                loaded=True
             else:
                 if self.click_checkBOX:
                     loaded=True
                     self.click_checkBOX=0
                 

  

        #self.ui.textEdit_6.setText(str(total_milliseconds))
        if self.__duration_<=position:
            loaded=True
            index_srt=0
    def on_btnSound_pressed(self):
        mute = self.audioOutput.isMuted()
        self.audioOutput.setMuted(not mute)
        if mute:
            self.ui.btnSound.setIcon(QIcon("images/volumn.bmp"))
        else:
            self.ui.btnSound.setIcon(QIcon("images/mute.bmp"))
    
    def on_sliderVolumn_valueChanged(self,value):
        self.audioOutput.setVolume(value/100)
    def on_sliderPosition_valueChanged(self,value):
        
        global index_srt
        global loaded
        if self.subtitles_==True:
            result = max([item["end_time"] for item in text_srt if item["end_time"] < value], default=None)
            #print(result)
            if result:
             max_index = next(i for i, v in enumerate(text_srt) if v["end_time"] == result)
             index_srt=max_index+1
             #print(index_srt)
            else:
                index_srt=0
                loaded=True
                self.ui.textEdit_1.setText("")
                self.ui.textEdit_2.setText("")
                self.ui.textEdit_3.setText("")
                self.ui.textEdit_4.setText("")
                self.ui.textEdit_5.setText("")
                self.ui.textEdit_6.setText("")
                self.ui.textEdit_7.setText("")
                self.ui.textEdit_8.setText("")
        else:
            _str_='无字幕'
            self.ui.textEdit_1.setText("")
            self.ui.textEdit_2.setText("")
            self.ui.textEdit_3.setText("")
            self.ui.textEdit_4.setText('<font color=\"#0000FF\">'+_str_+'</font>')
            self.ui.textEdit_5.setText("")
            self.ui.textEdit_6.setText("")
            self.ui.textEdit_7.setText("")
            self.ui.textEdit_8.setText("")            
        self.player.setPosition(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWidget = VideoPlay()
    myWidget.show()
    sys.exit(app.exec())