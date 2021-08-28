import urllib.request
import json
import time
import sys

status_strings = [None] * 18 # status strings dumped from RobloxPlayerBeta.exe
status_strings[0] = "Waiting for an available server"
status_strings[1] = "Server found, loading..."
status_strings[2] = "Joining server"
status_strings[3] = "This game is disabled"
status_strings[4] = "Cannot find game server"
status_strings[5] = "This game has ended"
status_strings[6] = "Requested game is full"
status_strings[7] = "Unknown Status 7"
status_strings[8] = "Unknown Status 8"
status_strings[9] = "Unknown Status 9"
status_strings[10] = "Followed user has left the game"
status_strings[11] = "This game is restricted"
status_strings[12] = "Not authorized to join this game"
status_strings[13] = "Server is busy"
status_strings[14] = "Hash Expired"
status_strings[15] = "Hash Exception"
status_strings[16] = "Your party is too large to fit"
status_strings[17] = "A Http error has occurred. Please close the client and try again."

last_print_raw = False
last_print_len = 0

def owcl(str): #OverWriteCurrentLine
    global last_print_raw
    global last_print_len
    curr_len = len(str)
    if last_print_len > curr_len:
        str = str.ljust(last_print_len, ' ')
    last_print_len = curr_len
    sys.stdout.write("\r%s" % str)
    sys.stdout.flush()
    last_print_raw = True

def println(str):
    global last_print_raw
    if last_print_raw:
        owcl("%s\n" % str)
        last_print_raw = False
    else:
        print(str)
    last_print_raw = False

def get_string_status(status):
    if status == None:
        return "None"
    if status > len(status_strings) or status < 0:
        return "Status out of range"
    else:
        return status_strings[status]

def create_request(url, data, cookie):
    return urllib.request.Request(url, method="POST", headers={
        "User-Agent": "Roblox/WinInet",
        "Content-Type": "application/json",
        "Requester": "Client",
        "PlayerCount": 0,
        "Cookie": ".ROBLOSECURITY=%s" % cookie
    }, data=data)

def keep_alive(req):
    last_status = 0
    last_job_id = None

    busy_streak = 0

    while True:
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read())
                jobid = None
                jobid_check = True
                if data["joinScript"]:
                    jobid = data["joinScript"]["GameId"]

                if data["status"] == 13: # Server busy
                    owcl("Server is busy, streak %d" % busy_streak)
                    time.sleep(5)
                    busy_streak += 1
                    last_status = data["status"]
                    continue

                if last_status == 13 and data["status"] != 13: # Server no longer busy
                    owcl("Server is no longer busy")
                    busy_streak = 0
                    last_status = data["status"]
                elif last_status != 2 and data["status"] == 2: # Server has started
                    if last_job_id == jobid:
                        owcl("Roblox moment")
                    else:
                        println("Server has started with jobId %s" % jobid)
                        jobid_check = False
                elif last_status != 0 and data["status"] == 0: # Server has shutdown
                    owcl("Server has shutdown")
                    jobid_check = False
                elif last_status != 5 and data["status"] == 5: # Server has ended
                    println("Server has ended")
                    jobid_check = False
                elif data["status"] == 2: # Server is running
                    owcl("Server is running")
                else:
                    if last_status != data["status"]: # The status has changed
                        println("Server status changed from %d to %d" % (last_status, data["status"]))
                    owcl(get_string_status(data["status"]))

                if jobid_check and last_job_id != jobid: # JobId has changed
                    println("Server status jobId changed from %s (%s) to %s (%s)" % (last_job_id, get_string_status(last_status), jobid, get_string_status(data["status"])))

                last_status = data["status"]
                last_job_id = jobid
        except urllib.error.HTTPError as e:
            owcl("Non 200 response code, it was %d" % e.code)
        except urllib.error.URLError as e:
            owcl("Non-HTTP error, err: %s" % e.reason)
        except Exception as e:
            println("whatever the fuck else gone wrong")
            print(e)

        time.sleep(1)