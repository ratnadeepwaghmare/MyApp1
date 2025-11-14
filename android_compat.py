import os
import sys

try:
    from android.storage import app_storage_path
    from android.permissions import request_permissions, Permission

    ANDROID = True
except ImportError:
    ANDROID = False


def is_android():
    return ANDROID


def android_fix_paths():
    if not ANDROID:
        return

    # Request necessary permissions
    request_permissions([
        Permission.CAMERA,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE
    ])


def get_android_database_path():
    if ANDROID:
        # Use app's internal storage on Android
        app_path = app_storage_path()
        db_dir = os.path.join(app_path, 'databases')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        return os.path.join(db_dir, 'gym_management.db')
    else:
        # Use current directory on desktop
        return 'gym_management.db'