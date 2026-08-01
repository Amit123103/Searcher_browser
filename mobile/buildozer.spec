[app]

# (str) Title of your application
title = Searcher Browser

# (str) Package name
package.name = searcherbrowser

# (str) Package domain (needed for android/ios packaging)
package.domain = com.searcher.browser

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,html,css,js,json,svg,ico

# (str) Application versioning
version = 1.3.0

# (list) Application requirements
requirements = python3,hostpython3,kivy,pyqt6,requests,urllib3,certifi,chardet,idna

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33
android.minapi = 21
android.ndk = 25b

# (str) Icon of the application
icon.filename = assets/logo.png

# (str) Presplash image
presplash.filename = assets/logo.png

[buildozer]
log_level = 2
warn_on_root = 1
