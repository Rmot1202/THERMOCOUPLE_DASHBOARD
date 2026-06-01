import json
import os
from datetime import datetime


class ProfileManager:
    """Manages machine profile storage and retrieval."""

    def __init__(self, profiles_dir="./profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)

    def save_profile(self, profile_name, config):
        safe_name = "".join(c for c in profile_name if c.isalnum() or c in ("-", "_"))
        if not safe_name:
            safe_name = f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        filepath = os.path.join(self.profiles_dir, f"{safe_name}.json")

        # Save the provided config as the profile JSON payload (flat config dict)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        return filepath

    def load_profile(self, profile_name):
        safe_name = "".join(c for c in profile_name if c.isalnum() or c in ("-", "_"))
        filepath = os.path.join(self.profiles_dir, f"{safe_name}.json")

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Profiles are stored as the raw config dict
            return data
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def list_profiles(self):
        profiles = []
        if os.path.exists(self.profiles_dir):
            for filename in os.listdir(self.profiles_dir):
                if filename.endswith(".json"):
                    profiles.append(filename[:-5])
        return sorted(profiles)

    def delete_profile(self, profile_name):
        safe_name = "".join(c for c in profile_name if c.isalnum() or c in ("-", "_"))
        filepath = os.path.join(self.profiles_dir, f"{safe_name}.json")

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting profile: {e}")

        return False