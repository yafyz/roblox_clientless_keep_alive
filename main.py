#!/usr/bin/env python3
import json
import gamejoin
import os
import argparse

base_url = "https://gamejoin.roblox.com"

def print_exit(str):
    print(str)
    exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--placeid", help="placeid of place to keep atleast one alive server on")
    parser.add_argument("--vip", help="access code to vip server to keep alive")
    parser.add_argument("--jobid", help="jobid of server to keep alive")
    parser.add_argument("--convid", help="conversation id for play together game")
    args = parser.parse_args()

    gamejoin_url = "/v1/join-game"
    rbody = {
        "placeId": args.placeid
    }
    if not "cookie" in os.environ:
        print_exit("No cookie varible in env")
    elif not args.placeid:
        print_exit("No placeId specified")

    if args.vip:
        print("PRIVATE-GAME")
        gamejoin_url = "/v1/join-private-game"
        rbody["accessCode"] = args.vip
    elif args.jobid:
        print("GAME-INSTANCE")
        gamejoin_url = "/v1/join-game-instance"
        rbody["gameId"] = args.jobid
    elif args.convid:
        print("PLAY-TOGETHER-GAME")
        gamejoin_url = "/v1/join-play-together-game"
        rbody["conversationId"] = args.convid
    else:
        print("GAME")

    req = gamejoin.create_request(base_url+gamejoin_url, bytes(json.dumps(rbody), "utf8"), os.environ["cookie"])

    gamejoin.keep_alive(req)

if __name__ == "__main__":
    main()