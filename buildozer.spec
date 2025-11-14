
[app]
title = LIbrary Management
package.name = gymmanagement
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.3.1
orientation = portrait

[buildozer]
log_level = 2

[android]
api = 30
minapi = 21
ndk = 21.4.7075529
permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA
