from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os, webbrowser
os.chdir(Path(__file__).resolve().parent)
server=ThreadingHTTPServer(('127.0.0.1',8080),SimpleHTTPRequestHandler)
print('Meydan: http://127.0.0.1:8080 - Durdurmak icin Ctrl+C')
webbrowser.open('http://127.0.0.1:8080')
server.serve_forever()
