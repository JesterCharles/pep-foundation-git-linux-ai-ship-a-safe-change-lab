"""Remove everything the lab created and restore the shipped starter files.

Run from the lab folder:  python tests/cleanup_lab.py
It removes the whole starter/ship-safe-change/ folder (including any file you added there) and
tests/__pycache__, after checking each path stays inside the lab, then rewrites the shipped files.
"""

from lab_support import reset_starter, restore_starter_files


def main():
    reset_starter()
    restore_starter_files()
    print("Lab cleaned: starter/ship-safe-change/ is back to its shipped files.")


if __name__ == "__main__":
    main()
