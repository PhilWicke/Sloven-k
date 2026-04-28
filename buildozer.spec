[app]
title = Slovenčk
package.name = slovencek
package.domain = org.slovencek
source.dir = src
source.include_exts = py,png,jpg,kv,json,mp3
version = 0.1.0
requirements = python3,kivy,pillow
orientation = portrait
fullscreen = 0

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
