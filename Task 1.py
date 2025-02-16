import requests
import time
import itertools

def fetch_users():
    """Fetches users from the API endpoint."""
    url = "https://snr-eng-7c5af300401d.herokuapp.com/api/users"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("users", [])
        else:
            print(f"Failed to fetch users. Status code: {response.status_code}")
            return []
    except Exception as e:
        print("Error fetching users:", e)
        return []

def normalize_value(value):
    """Normalize string values to enable consistent comparison."""
    if isinstance(value, str):
        return value.strip().lower()
    return value

def is_perfect_match(user1, user2):
    """
    Returns True if both users have matching dealbreaker values for the critical keys.
    This function compares only the keys that matter:
      - drinking
      - relationship_type
      - religion
      - smoking
      - wants_kids
    """
    keys = ["drinking", "relationship_type", "religion", "smoking", "wants_kids"]
    db1 = user1.get("dealbreakers", {})
    db2 = user2.get("dealbreakers", {})
    for key in keys:
        val1 = normalize_value(db1.get(key, ""))
        val2 = normalize_value(db2.get(key, ""))
        if val1 != val2:
            return False
    return True

def find_perfect_matches(users):
    """Finds all unique perfect matches based on the normalized dealbreaker fields."""
    perfect_matches = []
    for user1, user2 in itertools.combinations(users, 2):
        if is_perfect_match(user1, user2):
            dealbreakers = user1.get("dealbreakers", {})
            explanation = (
                f"Matching dealbreakers: drinking: {dealbreakers.get('drinking', 'N/A')}, "
                f"relationship_type: {dealbreakers.get('relationship_type', 'N/A')}, "
                f"religion: {dealbreakers.get('religion', 'N/A')}, "
                f"smoking: {dealbreakers.get('smoking', 'N/A')}, "
                f"wants_kids: {dealbreakers.get('wants_kids', 'N/A')}"
            )
            match = {
                "user1_id": user1["id"],
                "user1_name": user1["name"],
                "user2_id": user2["id"],
                "user2_name": user2["name"],
                "explanation": explanation
            }
            perfect_matches.append(match)
    print(f"Found {len(perfect_matches)} perfect matches.")
    for idx, match in enumerate(perfect_matches, start=1):
        print(f"Match {idx}: {match}")
    return perfect_matches

def validate_matches(matches):
    """
    Submits the matches in a batch to the validation endpoint and prints the response.
    The API expects only user1_id and user2_id for each match.
    """
    url = "https://snr-eng-7c5af300401d.herokuapp.com/api/validate-matches"
    payload = {
        "matches": [
            {"user1_id": m["user1_id"], "user2_id": m["user2_id"]} for m in matches
        ]
    }
    print("\nValidating batch payload:")
    print(payload)
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("Batch validation response:", result)
            if result.get("success"):
                print("Validation successful: All submitted matches are 100% compatible!")
            else:
                print("Validation failed: Some of the submitted matches are not perfectly compatible.")
            return result
        else:
            print(f"Validation failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print("Error during batch match validation:", e)
        return None

def debug_validate_matches(matches):
    """
    Validates each match individually and prints detailed debug information.
    This helps identify which individual match might be causing issues.
    """
    url = "https://snr-eng-7c5af300401d.herokuapp.com/api/validate-matches"
    valid_matches = []
    for idx, match in enumerate(matches, start=1):
        payload_single = {"matches": [{"user1_id": match["user1_id"], "user2_id": match["user2_id"]}]}
        print(f"\nValidating match {idx}: {match['user1_name']} & {match['user2_name']}")
        print("Payload:", payload_single)
        try:
            response = requests.post(url, json=payload_single)
            response_json = response.json()
            print("Response:", response_json)
            if response.status_code == 200 and response_json.get("success"):
                valid_matches.append(match)
            else:
                print("Match failed validation.")
        except Exception as e:
            print("Error validating match:", e)
        time.sleep(0.5)
    print(f"\nTotal individually validated matches: {len(valid_matches)}/{len(matches)}")
    return valid_matches

# Main execution
if __name__ == "__main__":
    users = fetch_users()
    if users:
        perfect_matches = find_perfect_matches(users)
        print("\nVerifying the matches with the batch validation endpoint...")
        batch_result = validate_matches(perfect_matches)
        print("\nNow debugging by validating each match individually...")
        valid_matches_debug = debug_validate_matches(perfect_matches)
    else:
        print("No users found. Exiting program.")