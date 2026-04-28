[app]
title = Slovencek
package.name = slovencek
package.domain = org.slovencek
source.dir = src
source.include_exts = py,png,jpg,kv,json,mp3,wav
source.exclude_dirs = __pycache__
version = 0.1.0
requirements = python3,kivy==2.3.1,pillow
orientation = portrait
fullscreen = 0
android.presplash_color = #F7F0E8

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
