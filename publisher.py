#!/usr/bin/env python
import requests
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


def main():
    challenge_url = "https://lrclib.net/api/request-challenge"
    publish_url = "https://lrclib.net/api/publish"

    # Get and solve the challenge
    print("Fetching the challenge...", end=" ")
    response = requests.post(challenge_url)
    challenge = response.json()

    print("Got it.")
    print("Solving the challenge...", end=" ")
    nonce = solve_challenge(challenge["prefix"], challenge["target"])
    print("Solved it.")

    # Publish the lyrics
    track_name = input("Track name? ")
    artist_name = input("Artist name? ")
    album_name = input("Album name? ")
    duration = int(input("Duration in seconds? "))

    with open("lyrics.txt", "r", encoding="utf-8") as f:
        plain_lyrics = f.read()

    with open("lyrics_synced.txt", "r", encoding="utf-8") as f:
        synced_lyrics = f.read()

    headers = {
        "X-Publish-Token": f"{challenge["prefix"]}:{nonce}",
        "Content-Type": "application/json"
    }

    data = {
        "trackName": track_name,
        "artistName": artist_name,
        "albumName": album_name,
        "duration": duration,
        "plainLyrics": plain_lyrics,
        "syncedLyrics": synced_lyrics,
    }

    print("Here's the data to publish. Press Enter to continue.")
    print()
    pprint(data)
    print()
    input()

    print("Publishing... ", end=" ")
    response = requests.post(publish_url, json=data, headers=headers)
    if response.status_code == 201:
        print("Successfully published!")
    else:
        print("Failed to publish. Error elaborated as follows:")
        pprint(response.json())


if __name__ == "__main__":
    main()
