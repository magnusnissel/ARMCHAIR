import tkinter as tk
import tkinter.ttk as ttk
import armchair
import multiprocessing as mp
import time
import datetime
import os
import sys


def repeated_worker(armchair, seconds, pipe):
    while True:
        pipe.send("Looking for new items...")
        num_new_items = armchair.index_items()
        msg = "Found {} new items.".format(num_new_items)
        pipe.send(msg)
        if num_new_items > 0:
            pipe.send("Downloading new items...")
            num_dl_items = armchair.grab_items()
            msg = "Downloaded {} items.".format(num_dl_items)
            pipe.send(msg)
            pipe.send("Extracting new items with jusText...")
            num_process_items = armchair.process_items()
            msg = "Processed {} items.".format(num_dl_items)
            pipe.send(msg)
            
        pipe.send("Done with this iteration. Waiting {} minutes...".format(int(seconds/60)))
        time.sleep(seconds)


def one_time_worker(armchair, pipe):
    pipe.send("Looking for new items...")
    num_new_items = armchair.index_items()
    msg = "Found {} new items.".format(num_new_items)
    pipe.send(msg)
    if num_new_items > 0:
        pipe.send("Downloading new items...")
        num_dl_items = armchair.grab_items()
        msg = "Downloaded {} items.".format(num_dl_items)
        pipe.send(msg)
        pipe.send("Extracting new items with jusText...")
        num_process_items = armchair.process_items()
        msg = "Processed {} items.".format(num_dl_items)
        pipe.send(msg)
    pipe.close()
 

class ComfyArmchair(tk.Frame):

    def __init__(self, root):
        tk.Frame.__init__(self)
        self.root = root
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.armchair = armchair.Armchair()
        self.draw_ui()
        self.root.mainloop()

    def maximize(self):
        toplevel = self.root.winfo_toplevel()
        try:  # Windows
            toplevel.wm_state('zoomed')
        except:  # Linux
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight() - 60
            geom_string = "%dx%d+0+0" % (w, h)
            toplevel.wm_geometry(geom_string)

    def draw_ui(self):
        self.root.title("ARMCHAIR Automated RSS Monitor Corpus Helper And Information Reporter")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="news")
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, style="StatusLabel.TLabel")
        self.status_bar.grid(column=0, row=1, sticky="news", padx=(10, 10), pady=(10, 10))
        self.book = ttk.Notebook(self)
        self.book.grid(column=0, row=0, sticky="news")
        self.run_frame = tk.Frame(self)
        self.setup_frame = tk.Frame(self)
        self.book.add(self.run_frame, text="Run")
        #self.book.add(self.setup_frame, text="Setup")
        self.setup_frame.rowconfigure(0, weight=1)
        self.setup_frame.columnconfigure(0, weight=1)
        self.run_frame.rowconfigure(0, weight=0)
        self.run_frame.rowconfigure(1, weight=0)
        self.run_frame.rowconfigure(2, weight=0)
        self.run_frame.rowconfigure(3, weight=1)
        self.run_frame.columnconfigure(0, weight=1)
        self.run_frame.columnconfigure(1, weight=1)
        self.run_once_button = ttk.Button(self.run_frame, command=self.run_once, text="Run once")
        self.run_repeated_button = ttk.Button(self.run_frame, command=self.run_repeated, text="Run repeatedly")
        self.run_once_button.grid(row=0, column=0, sticky="news", columnspan=2)
        self.run_repeated_button.grid(row=1, column=0, sticky="news", columnspan=2)
        ttk.Label(self.run_frame, text="Repetition interval (in minutes):").grid(row=2, column=0, sticky="news")
        self.interval_var = tk.IntVar()
        # to specify lower limit there needs to be an upper limit for some reason
        self.interval_spin = tk.Spinbox(self.run_frame, from_=1, to=sys.maxsize, textvariable=self.interval_var)  
        self.interval_var.set(5)
        self.interval_spin.grid(row=2, column=1, sticky="nes")
        self.log_text = tk.Text(self.run_frame)
        self.log_text.grid(row=3, column=0, sticky="news", columnspan=2)
        self.log_text["state"] = "disabled"
        self.pad_children(self.run_frame, 10, 10)



    @staticmethod
    def pad_children(parent, x=5, y=5):
        for child in parent.winfo_children():
            try:
                child.grid_configure(padx=x, pady=y)
            except tk.TclError:
                pass

    def update_status(self, text, ts=False, color=None, log=True):
        if ts:
            now = datetime.datetime.now().isoformat()[:19].replace("T"," ")
            text = "{} ({})".format(text, now)
        self.status_var.set(text)
        if log:
            self.log_text["state"] = "normal"
            self.log_text.insert("end", text)
            self.log_text.insert("end", "\n")
            self.log_text["state"] = "disabled"
        if color:
            self.status_bar.config(foreground=color)


    def check_job_status(self):
        stop = False
        self.root.update_idletasks()
        if not self.job.is_alive():
            stop = True
            self.job.terminate()
            self.update_status("Done.")
        else:
            if not self.stop_after:
                self.root.after(500, self.check_job_status)
                if self.run_mode == "repeated":
                    if self.pipe.poll():
                        self.last_msg = self.pipe.recv()
                        self.update_status(self.last_msg, ts=True)
                        self.root.update()
                else:
                    if self.pipe.poll(timeout=10):
                        self.last_msg = self.pipe.recv()
                        self.update_status(self.last_msg, ts=True)
                        self.root.update()

            else:
                if "Waiting" in self.last_msg:  #  only abort during wait 
                    self.job.terminate()
                    self.update_status("Stopped.", ts=True)
                    stop = True
                else:
                    self.root.after(500, self.check_job_status)
        if stop:
            self.run_once_button["state"] = "normal"
            self.run_repeated_button["state"] = "normal"
            self.root.update()

    def run_once(self):
        self.run_once_button["state"] = "disabled"
        self.run_repeated_button["state"] = "disabled"
        self.run_mode = "one-time"
        self.interval = self.interval_var.get()
        self.seconds = self.interval * 60
        self.stop_after = False
        self.pipe, worker_pipe = mp.Pipe()
        self.job = mp.Process(target=one_time_worker,
                         args=(self.armchair, worker_pipe))
        self.job.start()
        self.root.update_idletasks()
        self.root.after(500, self.check_job_status)
        
    def run_repeated(self):
        if self.run_repeated_button["text"] == "Run repeatedly":
            self.run_mode = "repeated"
            self.run_once_button["state"] = "disabled"
            self.run_repeated_button["text"] = "Stop during next wait"
            self.interval = self.interval_var.get()
            self.seconds = self.interval * 60
            self.stop_after = False
            self.pipe, worker_pipe = mp.Pipe()
            self.job = mp.Process(target=repeated_worker,
                             args=(self.armchair, self.seconds, worker_pipe))
            self.job.start()
            self.root.update_idletasks()
            self.root.after(500, self.check_job_status)
        else:
            self.update_status("Stopping soon...", ts=True)
            self.stop_after = True
            self.root.update()
            self.root.after(500, self.check_job_status)
            self.run_repeated_button["text"] = "Run repeatedly"
            self.run_repeated_button["state"] = "disabled"
            


def main():
    root = tk.Tk()
    app = ComfyArmchair(root)


if __name__ == "__main__":
    mp.freeze_support()
    main()