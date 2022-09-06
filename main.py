from tkinter import *
from tkinter import filedialog, ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import numpy as np
import cv2
import os
from datetime import datetime
import copy
import delete_old_files
import edit_page

buttons = [
'~','`','!','@','#','$','%','^','&','*','(',')','-','_','ENTER',
'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','\\','7','8','9','BACK',
'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l','[',']','4','5','6'
,'TAB',
'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.','?','/','1','2','3','SPACE',
]


class VideoPlayer(ttk.Frame):

    def __init__(self, parent: ttk.Frame=None, **prop: dict):
        setup = self.set_setup(prop)

        ttk.Frame.__init__(self, parent)

        # private
        self.__cap = object
        self.__size = (640, 480)
        self.__image_ratio = 480/640
        self.__frames_numbers = 0
        self.__play = False
        self.__frame = np.array
        self.__keyboard_mode = ""
        self.admin_password_entry=""
        self.admin_password="123"
        self.__initialdir = self.__initialdir_movie = os.path.join(os.getcwd(),'videos')
        self.video_folder_name = os.path.join(self.__initialdir,datetime.now().strftime("%Y-%m-%d"))
        if not os.path.exists(self.__initialdir):
            os.mkdir(self.__initialdir)
        if not os.path.exists(self.video_folder_name):
            os.mkdir(self.video_folder_name)
        self.__last_recorded_video = None
    
        # public
        self.frame = np.array
        # build widget
        self._build_widget(parent, setup)
        self.student_name = ""
        
        self.editpage = edit_page.EditPage(self)

    @property
    def frame(self)->np.array:
        return self.__frame

    @frame.setter
    def frame(self, frame: np.array):
        self.__frame = frame

    def set_setup(self, prop: dict)->dict:

        default = {'play':  True, 'replay': True,'camera': False, 'pause': True, 'stop': True, 'image': False, 'on' : True}
        setup = default.copy()
        setup.update(prop)
        return setup

    def _build_widget(self, parent: ttk.Frame=None, setup: dict=dict):

        # if parent is None:
        self.master.geometry("800x440+0+0")
        self.main_panel = Frame(self.master, relief=FLAT)
        self.main_panel.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

        # else:
        #     self.main_panel = parent

        # main panel
        self.main_panel.config(bg="black")

        icon_width = 45
        icon_height = 50
        canvas_progressbar_height = 2
        # frame_height = int(self.main_panel.cget('height')/10-icon_height-canvas_progressbar_height)

        self.canvas_image = Canvas(self.main_panel, bg="black", highlightthickness=0)
        self.canvas_image.pack(fill=BOTH, expand=True, side=TOP)
        self.canvas_image.bind("<Configure>", self.resize)

        self.board = Label(self.canvas_image, bg="black", width=44, height=14)
        self.board.pack(fill=BOTH, expand=True)

        canvas_progressbar = Canvas(self.main_panel, relief=FLAT, height=canvas_progressbar_height, 
                                    bg="black", highlightthickness=0)
        canvas_progressbar.pack(fill=X, padx=10, pady=10)

        s = ttk.Style()
        s.theme_use('clam')
        s.configure("red.Horizontal.TProgressbar", foreground='red', background='red', thickness=3)
        self.progressbar = ttk.Progressbar(canvas_progressbar, style="red.Horizontal.TProgressbar", orient='horizontal',
                                           length=200, mode="determinate")

        self.progressbar.pack(fill=X, padx=10, pady=10, expand=True)

        # control panel
        control_frame = Frame(self.main_panel, bg="black", relief=FLAT)
        control_frame.pack(side=BOTTOM, fill=X, padx=20)

        icons_path = os.path.abspath(os.path.join(os.getcwd(), 'icon'))

        # play camera
        if setup['camera']:
            self.icon_camera = PhotoImage(file=os.path.join(icons_path, 'camera.png'))
            button_camera = Button(control_frame, padx=10, pady=10, bd=8, fg="white", font=('arial', 12, 'bold'),
                                   text="camera", bg='black', image=self.icon_camera, height=icon_height,
                                   width=icon_width, command=lambda: self.camera_capture_with_recording())  
            button_camera.pack(side='left')
            
        if setup['on']:
            self.icon_on = PhotoImage(file=os.path.join(icons_path, 'display.png'))
            button_on = Button(control_frame, padx=10, pady=10, bd=8, fg="white", font=('arial', 12, 'bold'),
                                   text="on", bg='white', image=self.icon_on, height=icon_height,
                                   width=icon_width, command= lambda: self.camera_capture())  
            button_on.pack(side='right')
            
        if setup['pause']:
            # pause video button button_live_video
            self.icon_pause = PhotoImage(file=os.path.join(icons_path, 'pause2.png'))

            self.button_pause_video = Button(control_frame, padx=10, pady=10, bd=8, fg="white",
                                             font=('arial', 12, 'bold'),
                                             text="Pause", bg='black', image=self.icon_pause,
                                             height=icon_height, width=icon_width,
                                             command=lambda: self.pause_movie())
            self.button_pause_video.pack(side='left')


        if setup['stop']:
            # stop video button button_live_video
            self.icon_stop = PhotoImage(file=os.path.join(icons_path, 'stop.png'))
            button_stop_video = Button(control_frame, padx=10, pady=10, bd=8, fg="white", font=('arial', 12, 'bold'),
                                       text="stop", bg='black', height=icon_height, width=icon_width,
                                       image=self.icon_stop,
                                       command=lambda: self.stop_movie())
            button_stop_video.pack(side='left')

        if setup['replay']:
            # stop video button button_live_video
            self.icon_replay = PhotoImage(file=os.path.join(icons_path, 'replay.png'))
            button_replay_video = Button(control_frame, padx=10, pady=10, bd=8, fg="white", font=('arial', 12, 'bold'),
                                       text="stop", bg='black', height=icon_height, width=icon_width,
                                       image=self.icon_replay,
                                       command=lambda: self.replay_movie())
            button_replay_video.pack(side='left')

        if setup['play']:
            # play video button button_live_video
            self.icon_gallery = PhotoImage(file=os.path.join(icons_path, 'image.png'))
            self.icon_play = PhotoImage(file=os.path.join(icons_path, 'play2.png'))
            button_live_video = Button(control_frame, padx=10, pady=10, bd=8, fg="white", font=('arial', 12, 'bold'),
                                       text="> Load Video", bg='black', image=self.icon_gallery, height=icon_height,
                                       width=icon_width, command=lambda: self.load_movie())
            button_live_video.pack(side='right')

        # stop video button button_live_video
        self.icon_edit = PhotoImage(file=os.path.join(icons_path, 'edit.png'))
        button_edit_video = Button(control_frame, padx=10, pady=10, bd=8, fg="white", font=('arial', 12, 'bold'),
                                    text="stop", bg='black', height=icon_height, width=icon_width,
                                    image=self.icon_edit,
                                    command=lambda: self.edit())
        button_edit_video.pack(side='right')

        # # edit: create/delete file/folder/rename
        # self.icon_edit = PhotoImage(file=os.path.join(icons_path, 'edit.png'))
        # button_edit = Button(control_frame, padx=10, pady=10, bd=8, fg="white", font=('arial', 12, 'bold'),
        #                             text="stop", bg='black', height=icon_height, width=icon_width,
        #                             image=self.icon_edit,
        #                             command=lambda: self.edit())
        # button_edit.pack(side='left')

        # edit box
        self.frame_counter = Label(control_frame, height=2, width=15, padx=10, pady=10, bd=8,
                                   bg='black', fg="gray", font=('arial', 10, 'bold'))
        self.frame_counter.pack(side='left')

    def dialog(self):
        try:
            box.showinfo( 'Selection' , 'Your Choice: ' + \
            self.listbox.get( self.listbox.curselection() ) )
        except:
            box.showinfo( "Warning" , "Please select a file/folder")

    def delete(self):
        sel = self.listbox.curselection()
 
        # added reversed here so index deletion work for multiple selections.
        for index in reversed(sel):
            file_path = os.path.join(self.video_folder_name,os.listdir(self.video_folder_name)[index])

            msgbox = messagebox.askquestion('Delete','Are you sure you want to DELETE')
            if msgbox == 'yes':

                self.listbox.delete(index)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                box.showinfo( "Warning" , "Failed to delete %s\nReason: %s" %(file_path, e))

    def select(self,value):
        if value == "BACK":

            self.entry.delete(len(self.entry.get())-1,END)

        elif value == "TAB":
            self.entry.insert(END, '  ')
            
        elif value == "SPACE":
            self.entry.insert(END, ' ')
        elif value == "ENTER" and self.__keyboard_mode == "student_name":
            self.student_name = self.entry.get()
            self.window.destroy()

            self.video_folder_name = os.path.join(self.__initialdir,datetime.now().strftime("%Y-%m-%d"))
            self.current_time = datetime.now().strftime("%H-%M-%S")
            self.video_file_name = f"{self.current_time}_{self.student_name}.avi"
            self.pathname = os.path.join(self.video_folder_name,self.video_file_name)
            self.__last_recorded_video = self.pathname
            self.__cap = cv2.VideoCapture(0)
            self.__out = cv2.VideoWriter(self.pathname,cv2.VideoWriter_fourcc('M','J','P','G'), 8, (640,480))
            self.__frames_numbers = 1
            self.__play = not self.__play
            self.run_frames_with_recording()
            # return self.student_name
            
        elif value == "ENTER" and self.__keyboard_mode == "admin_password_edit":
            self.admin_password_entry = self.entry.get()
            if self.admin_password == self.admin_password_entry:
                self.window.destroy()
                
                self.editpage.show_editpage()
                
            else:
                self.window.destroy()
                # if cancel is pressed, destroy window; if retry is pressed, clear entry
                messagebox.askretrycancel(title="Prompt",message="Wrong Password!!") 
                                        

        elif value == "ENTER" and self.__keyboard_mode == "admin_password_load_movie":
            self.admin_password_entry = self.entry.get()
            self.window.destroy()
            if self.admin_password == self.admin_password_entry:
                
                movie_filename = filedialog.askopenfilename(initialdir=self.__initialdir_movie,
                                                            title="Select the movie to play",
                                                            filetypes=(("all files", "*.*"),
                                                                        ("AVI files", "*.avi"),
                                                                    ("MP4 files", "*.mp4")))
                #movie_filename = self.__last_recorded_video
                if len(movie_filename) != 0:
                    self.__initialdir_movie = os.path.dirname(os.path.abspath(movie_filename))

                    self.play_movie(movie_filename)

            else:
                # if cancel is pressed, destroy window; if retry is pressed, clear entry
                messagebox.askretrycancel(title="Prompt",message="Wrong Password!!")
                    
        else :
            self.entry.insert(END,value)

    def HosoPop(self):

        varRow = 2
        varColumn = 0

        for button in buttons:

            command = lambda x=button: self.select(x)
            
            if button == "SPACE" or button == "ENTER" or button == "TAB" or button == "BACK":
                Button(self.window,text= button,width=10,height=3,bg="#3c4987", fg="#ffffff",
                    activebackground = "#ffffff", activeforeground="#3c4987", relief='raised', padx=1,
                    pady=1, bd=1,command=command).grid(row=varRow,column=varColumn)

            else:
                Button(self.window,text= button,width=5, height=3,bg="#3c4987", fg="#ffffff",
                    activebackground = "#ffffff", activeforeground="#3c4987", relief='raised', padx=1,
                    pady=1, bd=1,command=command).grid(row=varRow,column=varColumn)


            varColumn +=1 

            if varColumn > 14 and varRow == 2:
                varColumn = 0
                varRow+=1
            if varColumn > 14 and varRow == 3:
                varColumn = 0
                varRow+=1
            if varColumn > 14 and varRow == 4:
                varColumn = 0
                varRow+=1

    def ask_entry(self,question):
        self.window = Toplevel(self)
        self.window.grab_set()
        self.window.geometry("800x440+0+0")
        # b = Button(text="hello",master=self.window)
        # b.pack()
        

        label1 = Label(self.window,text=question).grid(row=0,columnspan=15)

        # global entry
        self.entry = Entry(self.window,width=95)
        self.entry.grid(row=1,columnspan=20)
        # entry.pack()

        self.entry.bind("<Button-1>", lambda e: self.HosoPop())
        return self.entry

    def resize(self, event):

        w, h = event.width, event.height

        width = h/self.__image_ratio
        height = h

        if width > w:

            width = w
            height = w*self.__image_ratio

        self.__size = (int(width), int(height))
        if Image.isImageType(self.frame):
            image = copy.deepcopy(self.frame)
            self.show_image(image)

    def show_image(self, image):

        # resize image
        image.thumbnail(self.__size)
        #
        self.photo = ImageTk.PhotoImage(image=image)
        # The Label widget is a standard Tkinter widget used to display a text or image on the screen.
        self.board.config(image=self.photo)
        self.board.image = self.photo
        # refresh image display
        self.board.update()

    def replay_movie(self):
        
        # movie_filename = filedialog.askopenfilename(initialdir=self.__initialdir_movie,
        #                                             title="Select the movie to play",
        #                                             filetypes=(("AVI files", "*.AVI"),
        #                                                        ("MP4 files", "*.MP4"),
        #                                                        ("all files", "*.*")))
        try:
            movie_filename = self.__last_recorded_video
            if len(movie_filename) != 0:
                self.__initialdir_movie = os.path.dirname(os.path.abspath(movie_filename))
                self.play_movie(movie_filename)
            self.update_progress(0, 0)
        except:
            messagebox.showinfo(title=None, message="No prerecorded videos")

    def load_movie(self):
        
        self.__keyboard_mode = "admin_password_load_movie"
        self.__play = False
        self.admin_password_entry = ""
        self.admin_password_entry = self.ask_entry("Please insert admin password to proceed")
    
    def edit(self):
        
        self.__keyboard_mode = "admin_password_edit"
        self.__play = False
        self.admin_password_entry = ""
        self.admin_password_entry = self.ask_entry("Please insert admin password to proceed")

    def play_movie(self, movie_filename: str):
        self.__cap = cv2.VideoCapture(movie_filename)
        self.__frames_numbers = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.__image_ratio = self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH)

        self.progressbar["maximum"] = self.__frames_numbers
        self.__play = True
        self.run_frames()

    def run_frames(self):
        frame_pass = 0
        while self.__cap.isOpened():

            if self.__play:
                # update the frame number
                ret, image_matrix = self.__cap.read()
                # self.frame = image_matrix
                if ret:
                    frame_pass += 1
                    self.update_progress(frame_pass)

                    # convert matrix image to pillow image object
                    self.frame = self.matrix_to_pillow(image_matrix)
                    self.show_image(self.frame)
                    # self.__out.write(image_matrix)


                # refresh image display
            self.board.update()
        
        self.__cap.release()
        self.update_progress(0, 0)
        cv2.destroyAllWindows()
        
    def camera_capture(self):
        self.__play = False
        self.current_time = datetime.now().strftime("%H-%M-%S")
        self.video_file_name = f"{self.current_time}_{self.student_name}.avi"
        self.pathname = os.path.join(self.video_folder_name,self.video_file_name)
        self.__cap = cv2.VideoCapture(0)
        self.__play = not self.__play
        self.run_frames()

    def camera_capture_with_recording(self):
        self.__cap.release()
        self.__keyboard_mode = "student_name"
        self.__play = False
        self.student_name = ""
        self.student_name = self.ask_entry('Please insert your name')

    def run_frames_with_recording(self):
        frame_pass = 0
        while self.__cap.isOpened():

            if self.__play:
                # update the frame number
                ret, image_matrix = self.__cap.read()
                # self.frame = image_matrix
                if ret:
                    frame_pass += 1
                    self.update_progress(frame_pass)

                    # convert matrix image to pillow image object
                    self.frame = self.matrix_to_pillow(image_matrix)
                    self.show_image(self.frame)
                    self.__out.write(image_matrix)


                # refresh image display
            self.board.update()

        self.__cap.release()
        self.__out.release()

        cv2.destroyAllWindows()

    @staticmethod
    def matrix_to_pillow(frame: np.array):

        # convert to BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # convert matrix image to pillow image object
        frame_pillow = Image.fromarray(frame_bgr)
        return frame_pillow

    def stop_movie(self):

        self.pause_movie()
        self.__cap.release()
        
        cv2.destroyAllWindows()
        self.update_progress(0, 0)

    def pause_movie(self):

        if self.__cap.isOpened():
            self.__play = not self.__play

        else:
            self.__play = False
            

        if self.__play:
            self.button_pause_video.config(image=self.icon_pause)
        elif not self.__play:
            self.button_pause_video.config(image=self.icon_play)

    def update_progress(self, frame_pass: int=0, frames_numbers: int = None):

        if frames_numbers is None:
            frames_numbers = self.__frames_numbers

        self.frame_counter.configure(text=str(frame_pass) + " / " + str(frames_numbers))
        # update the progressbar
        self.progressbar["value"] = frame_pass
        self.progressbar.update()

if __name__ == "__main__":
    root_dir = os.path.join(os.getcwd(),"videos")
    log_dir = os.path.join(os.getcwd(),"logs")   #folder to delete log file
    limit_day = 14
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    #Current date
    # currentDate = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    delete_old_files.delete_old_files(root_dir,log_dir,limit_day)
    root = Tk()
    root.title("PiRecorder")
    VideoPlayer(root,image=True, play=True, camera=True, on=True).pack(side="top",fill="both",expand=True)
    edit_page.EditPage(root)
    root.mainloop()


