from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from livereload import Server

# Create FastAPI app
app = FastAPI()

# Mount your frontend folder (adjust path if needed)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    # Create livereload server wrapping FastAPI
    server = Server(app)

    # Watch all files in the frontend folder for changes
    server.watch("frontend/*.*")

    # Serve on port 8000, accessible from other devices on your network
    server.serve(host="0.0.0.0", port=8000, restart_delay=1)
