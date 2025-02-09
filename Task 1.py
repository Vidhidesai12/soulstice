# -*- coding: utf-8 -*-
"""Untitled11.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gsJcQ5VvwgWg3xWjomJezTgsPW6ek2fO
"""

import requests
import time

# Function to fetch users from the API
def fetch_users():
    url = 'https://snr-eng-7c5af300401d.herokuapp.com/api/users'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['users']  # Assuming the JSON response has a 'users' key
    else:
        print(f"Failed to fetch users. Status code: {response.status_code}")
        return []

# Helper function to check if two users are compatible based on dealbreakers
def is_compatible(user1, user2):
    return user1['dealbreakers'] == user2['dealbreakers']

# Generate potential perfect matches while avoiding duplicate pairings
# def find_perfect_matches(users):
#     perfect_matches = []
#     seen_pairs = set()  # Track checked pairs to avoid duplicates

#     for i, user1 in enumerate(users):
#         for j, user2 in enumerate(users):
#             if i < j:  # Ensure (A, B) is not repeated as (B, A)
#                 pair_key = frozenset([user1["id"], user2["id"]])
#                 if pair_key not in seen_pairs and is_compatible(user1, user2):
#                     seen_pairs.add(pair_key)  # Mark the pair as seen
#                     perfect_matches.append({
#                         "user1_id": user1["id"],
#                         "user1_name": user1["name"],
#                         "user2_id": user2["id"],
#                         "user2_name": user2["name"],
#                         "explanation": f"Both have matching dealbreakers: drinking: {user1['dealbreakers']['drinking']}, relationship_type: {user1['dealbreakers']['relationship_type']}, religion: {user1['dealbreakers']['religion']}, smoking: {user1['dealbreakers']['smoking']}, wants_kids: {user1['dealbreakers']['wants_kids']}"
#                     })

#     return perfect_matches

from itertools import combinations

def find_perfect_matches(users):
    perfect_matches = []

    for user1, user2 in combinations(users, 2):  # Generates unique (A, B) pairs
        if user1['dealbreakers'] == user2['dealbreakers']:  # Directly check compatibility
            dealbreakers_text = ", ".join(f"{k}: {v}" for k, v in user1['dealbreakers'].items())

            perfect_matches.append({
                "user1_id": user1["id"],
                "user1_name": user1["name"],
                "user2_id": user2["id"],
                "user2_name": user2["name"],
                "explanation": f"Both have matching dealbreakers: {dealbreakers_text}"
            })

    return perfect_matches


# Send the matches to the validate-matches endpoint
def validate_matches(matches):
    url = 'https://snr-eng-7c5af300401d.herokuapp.com/api/validate-matches'
    valid_matches = []
    match_number = 1  # Track match numbers

    for match in matches:
        response = requests.post(url, json={"matches": [match]})
        result = response.json()

        if result['success']:  # Only process valid matches
            valid_matches.append(match)
            print(f"Match {match_number}: {match['user1_name']} ({match['user1_id']}) and {match['user2_name']} ({match['user2_id']}) is valid!")
            print(f"Reason: {match['explanation']}")
            match_number += 1  # Increment match number

        time.sleep(1)  # Wait for 1 second between requests

    print(f"Total valid matches: {len(valid_matches)}")  # Print only the final valid count
    return valid_matches

# Main execution
users = fetch_users()  # Fetch users from the API
if users:
    matches = find_perfect_matches(users)
    valid_matches = validate_matches(matches)  # Validate matches and count only valid ones
else:
    print("No users found. Exiting program.")

