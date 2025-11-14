from kivy.config import Config

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')

# Import Android compatibility
try:
    from android_compat import android_fix_paths, get_android_database_path, is_android

    ANDROID = True
except ImportError:
    ANDROID = False

from gym_app import GymManagementApp

if __name__ == '__main__':
    # Initialize Android paths if on Android
    if ANDROID:
        android_fix_paths()

    GymManagementApp().run()