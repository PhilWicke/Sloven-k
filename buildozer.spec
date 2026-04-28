[app]
title = Slovencek
package.name = slovencek
package.domain = org.slovencek
source.dir = src
source.include_exts = py,png,jpg,kv,json,mp3,wav
source.exclude_dirs = __pycache__,.git
version = 0.1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.presplash_color = #F7F0E8

# Android specific
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
