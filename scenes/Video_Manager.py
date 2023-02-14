from asyncio.log import logger
from urllib.parse import ParseResultBytes
import os
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFile, ImageEnhance, ImageFilter
import textwrap
from nltk.tokenize import word_tokenize
from proglog import ProgressBarLogger, TqdmProgressBarLogger

class video_Manager:
    def __init__(self, user_key : str, project_key : str, background : int):
        self.user_key = user_key
        self.project_key = project_key
        self.background = background
        self.project_dir = os.getcwd().replace("\\", "/") + "/projects/" + self.user_key + "/" + self.project_key + "/sources"
        self.present_task = 0
    
    def convert_pages(self):
        page_dir = self.project_dir + "/pages"
        gif_dir = self.project_dir + "/GIF"
        voice_dir = self.project_dir + "/voices"
        list_of_voices = os.listdir(voice_dir)
        ind_tmp = []
        for voice in list_of_voices:
            if self.project_key in voice:
                index = voice.replace(self.project_key, '').replace('voice','').replace(".mp3",'').replace('_','')
                ind_tmp.append(index)
                
        
        if not os.path.exists(gif_dir):
            os.mkdir(gif_dir)
            
        
        for page in ind_tmp:
            frames = []
            voice_path = self.project_dir + "/voices/" + self.project_key + "_voice_" + page + ".mp3"
            print(voice_path)
            audioclip = AudioFileClip(voice_path).audio_fadeout(1)
            duration = audioclip.duration
            image = Image.open(page_dir + "/" + "page_img" + page + ".png")

            frames.append(image) 

            frames[0].save(gif_dir+ "/" + "page_img" + page + ".gif", format='GIF',
               append_images=frames[1:], save_all=True, duration = duration * 1000 )

            image.close()
            audioclip.close() 
            
    def synthesis_GIF(self):
        gif_clips = []
        page_dir = self.project_dir + "/GIF"
        gif_list = os.listdir(page_dir)
        for file in gif_list:
            if ".gif" in file:
                print(file)
                gif = VideoFileClip(page_dir + "/" + file)
                gif_clips.append(gif)
                

        final_frames = concatenate_videoclips(gif_clips, method="compose")
        message = "GIF 합성 중"
        self.present_task = 4
        path = os.getcwd().replace("\\", "/") + "/projects/" + self.user_key + "/" + self.project_key + "/"
        my_logger = MyBarLogger(msg=message, present_task=str(self.present_task), path = path)
        final_frames.write_videofile(self.project_dir + "/{}_final_frame.mp4".format(self.project_key), fps=30, remove_temp=True, threads=12, codec = 'libx264', logger = my_logger)

    def synthesis_voices(self):
        voice_dir = self.project_dir + "/voices"
        voices = os.listdir(voice_dir)
        voice_tmp = []
        print(voices)
        for voice in voices:
            if ".mp3" in voice:
                voice_path = voice_dir + "/" + voice
                print(voice_path)
                voice_page = AudioFileClip(voice_path).audio_fadeout(1)
                voice_tmp.append(voice_page)
        
        final_audio = concatenate_audioclips(voice_tmp)
        message = "음성 합성 중"
        self.present_task = 3
        print("{}_final_voice.mp3".format(self.project_key))
        path = os.getcwd().replace("\\", "/") + "/projects/" + self.user_key + "/" + self.project_key + "/"
        my_logger = MyBarLogger(msg=message, present_task=str(self.present_task), path=path)
        final_audio.write_audiofile(self.project_dir + "/{}_final_voice.mp3".format(self.project_key), logger = my_logger)
    
    def synthesis_intro(self):
        
        pass
    
    def synthesis_outro(self):
        pass
    
    def synthesis_final(self):
        voice_dir = self.project_dir + "/voices"
        page_dir = self.project_dir + "/pages"
        message = "최종 영상 합성 중"
        
        self.present_task = 5
        path = os.getcwd().replace("\\", "/") + "/projects/" + self.user_key + "/" + self.project_key + "/"

        my_logger = MyBarLogger(msg=message, present_task=str(self.present_task), path=path)
        print("{}_final_voice.mp3".format(self.project_key))
        voice = AudioFileClip(self.project_dir + "/{}_final_voice.mp3".format(self.project_key))
        video_without_voice = VideoFileClip(self.project_dir + "/{}_final_frame.mp4".format(self.project_key)).set_audio(voice)
        video_without_voice.write_videofile(self.project_dir + "/{}_final_video.mp4".format(self.project_key), fps=30, threads = 12, remove_temp = True, codec = 'libx264', audio_codec = 'aac', logger = my_logger)

        voice.close()
        video_without_voice.close()
    
class GUILogger(ProgressBarLogger):

    def callback(self, **changes):
        # Every time the logger is updated, this function is called with
        # the `changes` dictionnary of the form `parameter: new value`.
        
        for (parameter, new_value) in changes.items():
            print(changes)

class MyBarLogger(TqdmProgressBarLogger):
    def __init__(self, init_state=None, bars=None, leave_bars=False, ignored_bars=None, logged_bars='all', notebook='default', print_messages=True, min_time_interval=0, ignore_bars_under=0, path ='', total_task = "5", present_task = "0", msg = ""):
        super().__init__(init_state, bars, leave_bars, ignored_bars, logged_bars, notebook, print_messages, min_time_interval, ignore_bars_under)
        
        try:
            self.msg = msg.decode("utf-8")
        except:
            self.msg = msg

        self.path = path
    
        self.msg = self.msg.replace("b", "").replace("'", "")

        try:
            self.total_task = total_task.decode("utf-8")
        except:
            self.total_task = total_task

        try:
            self.now_task = present_task.decode("utf-8")
        except:
            self.now_task = present_task

    def callback(self, **changes):
        # Every time the logger is updated, this function is called        
        if len(self.bars):
            f = open(self.path + "/" + "logger.txt", 'w', encoding="UTF-8")

            percentage = next(reversed(self.bars.items()))[1]['index'] / next(reversed(self.bars.items()))[1]['total']
            
            f.write(str(percentage * 100) + "|" + self.msg +"|"+self.now_task+"/"+self.total_task)

            f.close()
