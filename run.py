import os
from dotenv import load_dotenv

# Explicit path so the .env is found regardless of where the script is invoked from
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app import create_app, start_background_watcher

app = create_app()

if __name__ == '__main__':
    start_background_watcher(app)
    app.run(debug=True, use_reloader=False)
