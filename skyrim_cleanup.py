import os
import shutil
import sys

# List of required base game files and folders for SkyrimVR
BASE_GAME_FILES = {
    "SkyrimVR.exe",
    "steam_api64.dll",
    "binkw64.dll",
    "atimgpud.dll",
    "High.ini",
    "Medium.ini",
    "Low.ini",
    "Skyrim.ini",
    "openvr_api.dll",
    "installscript.vdf",
    "Data",  # Folder
}

# Use environment variables and universally accessible folders
PROTECTED_FOLDERS = [
    os.getenv("PROGRAMFILES"),
    os.getenv("PROGRAMFILES(X86)"),
    os.getenv("SYSTEMDRIVE") + "\\Windows",
    os.path.join(os.getenv("SYSTEMDRIVE"), "Users"),
    os.getenv("ALLUSERSPROFILE"),
    os.getenv("APPDATA"),
    os.getenv("LOCALAPPDATA"),
    os.path.join(os.getenv("USERPROFILE"), "Desktop"),
    os.path.join(os.getenv("USERPROFILE"), "Documents")
]

def log(message):
    """Log a message to the terminal."""
    print(f"[INFO] {message}")

def scan_entire_pc():
    """Scan the entire PC for the SkyrimVR folder."""
    log("Scanning the entire PC for SkyrimVR...")
    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if os.path.exists(f"{drive}:\\"):
            log(f"Scanning drive {drive}:\\...")
            for root, dirs, files in os.walk(f"{drive}:\\"):
                if "SkyrimVR.exe" in files:
                    log(f"SkyrimVR installation found: {root}")
                    return root
    return None

def scan_drive(drive_letter):
    """Scan a specific drive for the SkyrimVR folder."""
    log(f"Scanning drive {drive_letter}: for SkyrimVR...")
    for root, dirs, files in os.walk(f"{drive_letter}:\\"):
        if "SkyrimVR.exe" in files:
            log(f"SkyrimVR installation found: {root}")
            return root
    return None

def find_skyrim_vr():
    """Find the SkyrimVR folder based on the user's choice."""
    log("Choose an option:")
    log("1. Scan the entire PC")
    log("2. Provide a drive letter to scan (e.g., C)")
    log("3. Provide the full path to SkyrimVR (e.g., A:\\SteamLibrary\\steamapps\\common\\SkyrimVR)")

    choice = input("Enter your choice (1/2/3): ").strip()
    if choice == "1":
        return scan_entire_pc()
    elif choice == "2":
        drive_letter = input("Enter the drive letter (e.g., C): ").strip().upper()
        if not os.path.exists(f"{drive_letter}:\\"):
            log(f"Drive {drive_letter}: does not exist.")
            return None
        return scan_drive(drive_letter)
    elif choice == "3":
        path = input("Enter the full path to SkyrimVR: ").strip()
        if os.path.exists(path) and "SkyrimVR.exe" in os.listdir(path):
            log(f"SkyrimVR installation found: {path}")
            return path
        log("Invalid path or SkyrimVR.exe not found in the provided directory.")
        return None
    else:
        log("Invalid choice. Please restart the script and try again.")
        input("Press any key to exit...")  # Wait for user input before closing
        sys.exit(1)

def warn_if_in_protected_folders(folder):
    """Warn the user if the folder is in a Windows protected folder."""
    for protected_folder in PROTECTED_FOLDERS:
        if protected_folder and folder.lower().startswith(protected_folder.lower()):
            log(f"WARNING: SkyrimVR is installed in a restricted folder: {folder}")
            log("Remember, this directory is not optimal for modded SkyrimVR and may cause unknown issues.")
            if get_user_confirmation("Do you want to proceed with cleaning the directory despite the risks?"):
                if get_user_confirmation("Do you want to see recommended safe and bad install locations?"):
                    show_protected_folders_list()
                return
            else:
                input("Press any key to exit...")  # Wait for user input before closing the script
                sys.exit(1)

def get_user_confirmation(prompt):
    """Prompt the user for a Yes/No answer."""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            log("Invalid response. Please enter 'y' or 'n'.")

def show_protected_folders_list():
    """Show a list of protected folders and safe install locations."""
    log("\nProtected directories to avoid when installing SkyrimVR:")
    for protected_folder in PROTECTED_FOLDERS:
        if protected_folder:
            log(f"- {protected_folder}")
    
    log("\nSuggested safe install locations:")
    log("- C:\\SteamLibrary\\steamapps\\common\\SkyrimVR")
    log("- D:\\SteamLibrary\\steamapps\\common\\SkyrimVR")
    log("- E:\\SteamLibrary\\steamapps\\common\\SkyrimVR")
    log("- F:\\SteamLibrary\\steamapps\\common\\SkyrimVR")

def verify_files(folder):
    """Verify the files in the SkyrimVR folder."""
    log("Verifying files in the SkyrimVR folder...")
    found_files = set(os.listdir(folder))
    extra_files = found_files - BASE_GAME_FILES
    missing_files = BASE_GAME_FILES - found_files

    if missing_files:
        log("Missing files detected:")
        for file in missing_files:
            log(f"- {file}")
        log("To fix this, open Steam, go to your library, right-click SkyrimVR, and select 'Properties'.")
        log("Then, navigate to 'Local Files' and click 'Verify integrity of game files'.")
    else:
        log("All base game files are present.")

    if extra_files:
        log("Extra files detected:")
        for file in extra_files:
            log(f"- {file}")
    
    return extra_files, missing_files

def remove_extra_files(folder, extra_files):
    """Remove extra files and folders from the folder."""
    log("Removing extra files and folders...")
    for file in extra_files:
        file_path = os.path.join(folder, file)
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Recursively remove directories
            else:
                os.remove(file_path)
            log(f"Deleted: {file}")
        except Exception as e:
            log(f"Failed to delete {file}: {e}")

def enforce_clean_directory(folder):
    """Ensure only whitelisted files and folders are present in the directory."""
    log("Enforcing clean directory policy...")
    found_files = set(os.listdir(folder))
    non_whitelisted_items = found_files - BASE_GAME_FILES

    if non_whitelisted_items:
        log("Non-whitelisted files and folders detected:")
        for item in non_whitelisted_items:
            log(f"- {item}")
        if get_user_confirmation("Do you want to delete these non-whitelisted items?"):
            remove_extra_files(folder, non_whitelisted_items)
            log("Directory cleaned successfully.")
        else:
            log("Non-whitelisted items were not removed.")

def main():
    log("Welcome to the SkyrimVR cleanup and verification script.")
    
    skyrim_folder = find_skyrim_vr()
    if not skyrim_folder:
        log("No SkyrimVR installation found. Exiting script.")
        input("Press any key to exit...")  # Wait for user input before closing
        sys.exit(1)
    
    warn_if_in_protected_folders(skyrim_folder)
    
    extra_files, missing_files = verify_files(skyrim_folder)
    
    if extra_files:
        log("Extra files detected:")
        for file in extra_files:
            log(f"- {file}")
        if get_user_confirmation("Do you want to delete these extra files?"):
            remove_extra_files(skyrim_folder, extra_files)
            log("Extra files have been removed.")
        else:
            log("Extra files were not removed.")

    enforce_clean_directory(skyrim_folder)
    
    log("Script completed.")
    input("Press any key to exit...")  # Wait for user input before closing
    sys.exit(0)

if __name__ == "__main__":
    main()
