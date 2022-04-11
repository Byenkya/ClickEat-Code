import os
import time
import pipes

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

DB_HOST  = "127.0.0.1" #os.environ["DATABASE_ADDRESS"]
DB_USER = os.environ["DATABASE_USER"]
DB_USER_PASSWORD = os.environ["DATABASE_USER_PASSWORD"]

#DB_NAME = '/backup/dbackup'
DB_NAME = os.environ["DATABASE_NAME"] #'database_backup'
BACKUP_PATH = os.path.dirname(os.path.abspath(__file__)) + '/back_up'

# Getting current Date Time To create  the separate back folder
DATETIME = time.strftime("%Y%m%d-%H%M%S")
TODAY_BACKUP_PATH = BACKUP_PATH + '/' + DATETIME

# def save_to_drive():
#     for file in os.listdir(TODAY_BACKUP_PATH):
#         f = drive.CreateFile({'click_eat_back_up' : file})
#         f.SetContentFile(os.path.join(TODAY_BACKUP_PATH, file))
#         f.Upload()
#         # due to unknown bug in pydrive if we
#         # Due to a known bug in pydrive if we 
#         # don't empty the variable used to
#         # upload the files to Google Drive the
#         # file stays open in memory and causes a
#         # memory leak, therefore preventing its 
#         # deletion
#         f = None
    
#     for file in os.listdir(TODAY_BACKUP_PATH):
#         os.remove(os.path.join(TODAY_BACKUP_PATH, file))

# checking the backup folder already exists or not. If not exists will create it.
try:
    os.stat(TODAY_BACKUP_PATH)
except:
    os.mkdir(TODAY_BACKUP_PATH)

# Code for checking if you want to take single database backup or assined multiple backups.
print("checking for databases names file.")

if os.path.exists(DB_NAME):
    file1 = open(DB_NAME)
    multi = 1
    print("Databases file found...")
    print("Starting backup of database" + DB_NAME)

else:
    print("Database file not found...")
    print("Starting backup of database " + DB_NAME)
    multi = 0

# starting actual database backup process
if multi:
    in_file = open(DB_NAME, "r")
    f_lenght = len(in_file.readlines())
    in_file.close()
    p = 1
    db_file = open(DB_NAME, "r")

    while p <= f_lenght:
        db = db_file.readline() # reading database names from file
        db = db[:-1]
        dumpcmd = "mysqldump - h" + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " --databases " \
            + db + " > " + pipes.quote(TODAY_BACKUP_PATH) + "/" + db + ".sql"
        os.system(dumpcmd)
        gzipcmd = "gzip " + pipes.quote(TODAY_BACKUP_PATH) + "/" + db + ".sql"
        os.system(gzipcmd)
        p = p + 1

    db_file.close()

else:
    db = DB_NAME
    dumpcmd = "mysqldump -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD \
        + " --databases " + db + " > " + pipes.quote(TODAY_BACKUP_PATH) + "/" + db + ".sql"  
    os.system(dumpcmd)
    gzipcmd = "gzip " + pipes.quote(TODAY_BACKUP_PATH) + "/" + db + ".sql"
    os.system(gzipcmd)
    # save_to_drive()

print("")
print("Backup script completed")
print("Your backups have been created in '" + TODAY_BACKUP_PATH + "' directory")

