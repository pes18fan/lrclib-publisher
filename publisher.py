#!/usr/bin/env python
import requests
import tkinter as tk
from tkinter import ttk, N, W, E, S
from hashlib import sha256
from pprint import pprint


def verify_nonce(result: bytes, target: bytes) -> bool:
    if len(result) != len(target):
        return False

    for i in range(0, len(result)):
        if result[i] > target[i]:
            return False
        elif result[i] < target[i]:
            break

    return True


def solve_challenge(prefix: str, target_hex: str) -> str:
    nonce = 0
    target = bytes.fromhex(target_hex)

    while True:
        payload = prefix + str(nonce)
        hashed = sha256(payload.encode()).digest()

        result = verify_nonce(hashed, target)
        if result:
            break
        else:
            nonce += 1

    return str(nonce)


def publish(*args):
    synced_lyrics = synced_lyrics_entry.get("1.0", "end-1c")
    plain_lyrics = plain_lyrics_entry.get("1.0", "end-1c")

    challenge_url = "https://lrclib.net/api/request-challenge"
    publish_url = "https://lrclib.net/api/publish"

    status.set("Solving LRCLib's proof-of-work challenge...")

    # Get and solve the challenge
    print("Fetching the challenge...", end=" ")
    response = requests.post(challenge_url)
    challenge = response.json()

    print("Got it.")
    print("Solving the challenge...", end=" ")
    nonce = solve_challenge(challenge["prefix"], challenge["target"])
    print("Solved it.")

    headers = {
        "X-Publish-Token": f"{challenge["prefix"]}:{nonce}",
        "Content-Type": "application/json"
    }

    data = {
        "trackName": track.get(),
        "artistName": artist.get(),
        "albumName": album.get(),
        "duration": int(duration.get()),
        "plainLyrics": plain_lyrics,
        "syncedLyrics": synced_lyrics,
    }

    status.set("Publishing...")
    response = requests.post(publish_url, json=data, headers=headers)
    if response.status_code == 201:
        status.set("Successfully published!")
    else:
        status.set("Failed to publish. Error elaborated in console.")
        print(f"Status: {response.status_code}")
        pprint(response.json())


root = tk.Tk()
root.title("LRCLib Publisher")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Track, artist, album
track = tk.StringVar()
ttk.Label(mainframe, text="Track:").grid(column=1, row=1, sticky=W)
track_entry = ttk.Entry(mainframe, width=10, textvariable=track)
track_entry.grid(column=2, row=1, sticky=(W, E))

artist = tk.StringVar()
ttk.Label(mainframe, text="Artist:").grid(column=1, row=2, sticky=W)
artist_entry = ttk.Entry(mainframe, width=10, textvariable=artist)
artist_entry.grid(column=2, row=2, sticky=(W, E))

album = tk.StringVar()
ttk.Label(mainframe, text="Album:").grid(column=1, row=3, sticky=W)
album_entry = ttk.Entry(mainframe, width=10, textvariable=album)
album_entry.grid(column=2, row=3, sticky=(W, E))

duration = tk.StringVar()
ttk.Label(mainframe, text="Duration in seconds:").grid(column=1, row=4, sticky=W)
duration_entry = ttk.Entry(mainframe, width=10, textvariable=duration)
duration_entry.grid(column=2, row=4, sticky=(W, E))

# Synced lyrics field
ttk.Label(mainframe, text="Synced lyrics:").grid(column=1, row=5, sticky=W)
synced_lyrics_entry = tk.Text(mainframe, height=10, width=10)
synced_lyrics_entry.grid(column=2, row=5, sticky=(W, E))

# Unsynced lyrics field
ttk.Label(mainframe, text="Unsynced lyrics:").grid(column=1, row=6, sticky=W)
plain_lyrics_entry = tk.Text(mainframe, height=10, width=20)
plain_lyrics_entry.grid(column=2, row=6, sticky=(W, E))

ttk.Button(mainframe, text="Publish", command=publish).grid(column=2, row=7, sticky=W)

status = tk.StringVar()
status.set("Waiting for you to publish...")
ttk.Label(mainframe, textvariable=status).grid(column=1, row=8)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

track_entry.focus()

root.mainloop()
