import asyncio
import websockets
import json
import argparse
from pytz import timezone
from datetime import datetime
from termcolor import colored

async def handle_message(message, verbose, keywords, log):
  try:
    message = json.loads(message)
    did = message["did"]
    kind = message["kind"]
    time = message["time_us"]
    # Can filter older things still in the firehose (UNIX time)
    # if time < 1732220335962062:
    #   return
    if kind == "commit":
      commit = message["commit"]
      rkey = commit["rkey"]
      operation = commit["operation"]
      if operation != "create":
        return
      url = f"https://bsky.app/profile/{did}/post/{rkey}"
      utc_time = datetime.fromtimestamp((time / 1000000), timezone("UTC"))
      pacific_time = utc_time.astimezone(timezone("US/Pacific"))
      pretty_time = pacific_time.strftime("%H:%M:%S")
      record = commit["record"]
      text = record["text"]
      # CAN FILTER FOR SHIT
#      if "pawg" not in text and "hack" not in text:
#        return
      print(colored(url, "green", attrs=["bold"]))
      print(colored(pretty_time, "blue", attrs=["bold"]), end=" | ")
      if "reply" in commit["record"]:
        print(colored("REPLY", "white", attrs=["bold"]), end=" | ")
      else:
        print(colored("POST", "white", attrs=["bold"]), end=" | ")
      if "embed" in commit["record"]:
        # has images and embed
        embed = commit["record"]["embed"]["$type"].replace("app.bsky.embed.", "").upper()
        print(colored(embed, "yellow", attrs=["bold"]), end=" | ")
      if len(keywords):
        has_keyword = any(keyword in text for keyword in keywords)
        if has_keyword:
          print(colored(text, "red"))
        else:
          print(text)
      else:
        print(text)

      if verbose:
        print(message)
      print()
      if log:
        with open("log.txt", "a") as log_file:
          log_file.write(url + "\n")
          log_file.write(pretty_time + " | ")
          log_file.write(text + "\n\n")
  except json.JSONDecodeError as e:
    print(f"Error decoding message:\n{msg}\n{e}")


async def listen_to_websocket(verbose, keywords, log):
  async with websockets.connect(URI) as websocket:
    while True:
      try:
        message = await websocket.recv()
        await handle_message(message, verbose, keywords, log)
      except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")
        break
      except Exception as e:
        print(f"Error: {e}")


URI = "wss://jetstream2.us-west.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"

parser = argparse.ArgumentParser(description='BlueSky Firehose')
parser.add_argument('--log', action='store_true', help='If set, store results in log.txt. If keywords we only save matched content.')
parser.add_argument('--verbose', action='store_true', help='Print entire JSON for each message.')
parser.add_argument('--keywords', default=[], nargs='*', help='A space-separated list of keywords')
args = parser.parse_args()

asyncio.get_event_loop().run_until_complete(listen_to_websocket(args.verbose, args.keywords, args.log))
