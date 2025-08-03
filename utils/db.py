import os
import json

# ✅ Database folder & file paths
DB_FOLDER = "database"
DB_FILE = os.path.join(DB_FOLDER, "data.json")

# ✅ Initialize DB (create folder & file if not exist)
def init_db():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

# ✅ Read data from DB
def read_db():
    if not os.path.exists(DB_FILE):
        init_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)

# ✅ Write data to DB
def write_db(data):
    if not os.path.exists(DB_FILE):
        init_db()
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ✅ Update a specific key in DB
def update_db(key, value):
    data = read_db()
    data[key] = value
    write_db(data)

# ✅ Get value of a specific key
def get_db_value(key, default=None):
    data = read_db()
    return data.get(key, default)
