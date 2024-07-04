import uvicorn
from fastapi import FastAPI


class Server:

    def __init__(
            self, 
            host: str, 
            port: int
            ) -> None:
        
        self.host = host
        self.port = port
        self.app = FastAPI()

    def run(self):
        uvicorn.run(self.app, host=self.host, port=self.port)