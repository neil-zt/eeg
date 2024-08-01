import os
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time

class FolderMonitor(threading.Thread):
    def __init__(self, server, folder_path, folder_name):
        threading.Thread.__init__(self)
        self.server = server
        self.folder_path = folder_path
        self.folder_name = folder_name
        self.stop_flag = threading.Event()

    def run(self):
        while not self.stop_flag.is_set():
            files_in_folder = [f for f in os.listdir(self.folder_path) if os.path.isfile(os.path.join(self.folder_path, f))]
            if len(files_in_folder) >= self.server.num_files:
                self.server.add_subfolder(self.folder_name)
                print(f"Folder {self.folder_name} added to subfolders list")
                break
            time.sleep(0.1)  # Check every second

    def stop(self):
        self.stop_flag.set()

class NewFolderHandler(FileSystemEventHandler):
    def __init__(self, server):
        self.server = server
        self.monitors = {}

    def on_created(self, event):
        if event.is_directory:
            new_folder_name = os.path.basename(event.src_path)
            print(f"New folder detected: {new_folder_name}")
            
            monitor = FolderMonitor(self.server, event.src_path, new_folder_name)
            self.monitors[new_folder_name] = monitor
            monitor.start()

class Server:

    def __init__(self, host: str, port: int, num_files: int = 1) -> None:
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.setup_cors()
        self.subfolders = []
        self.output_destination = None
        self.define_routes()
        self.observer = None
        self.last_processed_subfolder = None
        self.num_files = num_files

    def setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def define_routes(self):

        @self.app.get("/status")
        async def get_status():
            return {
                "status": "ready",
                "output_destination": self.output_destination,
            }
        
        @self.app.get("/latest")
        async def get_latest():
            if not self.subfolders:
                return {"empty": True}
            
            latest_folder_name = self.subfolders[-1]
            if latest_folder_name == self.last_processed_subfolder:
                return {"empty": True}
            self.last_processed_subfolder = latest_folder_name
            
            latest_folder_path = os.path.join(self.output_destination, latest_folder_name)
            
            png_files = [f for f in os.listdir(latest_folder_path) if f.endswith('.png')]
            images_base64 = {}
            for png_file in png_files:
                png_path = os.path.join(latest_folder_path, png_file)
                with open(png_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    images_base64[png_file] = encoded_string
                    
            return {"images": images_base64}

    def inject_output_destination_name(self, output_destination):
        self.output_destination = output_destination
        if not os.path.exists(self.output_destination):
            os.makedirs(self.output_destination)
        self.start_monitoring()

    def start_monitoring(self):
        event_handler = NewFolderHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.output_destination, recursive=False)
        self.observer.start()

    def add_subfolder(self, folder_name):
        self.subfolders.append(folder_name)

    def run(self):
        try:
            uvicorn.run(self.app, host=self.host, port=self.port)
        except KeyboardInterrupt:
            if self.observer:
                self.observer.stop()
                self.observer.join()

    def __del__(self):
        if hasattr(self, 'observer') and self.observer:
            self.observer.stop()
            self.observer.join()