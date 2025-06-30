# HueForge-Translations
Public Repository for adding new HueForge translation files.

Most of the HueForge translation files are .ts files which are the Qt specific format of translations.
They are an XML format and QtLinguist is the easiest tool to use when manipulating them, but you can
do it with other tools.

There is a GitHub repo for QtLinguist as well as other ways to get it.  Qt also maintains localization files for QtLinguist
You can get Windows exes by themselves here: https://github.com/thurask/Qt-Linguist
I don't have a location aside from downloadings straight from the Qt Maintenance tool for MacOS or Linux yet.  I will add one as I find one.

The main translation file is HueForge_en.ts which is the most recent set of untranslated English strings.  You should take this file and rename it
to your desired language such as HueForge_ja.ts for Japanese.

Use the format HueForge_ll_username.ts 
ll is the 2 character abbreviation (or 4 for cases like es-MX or zh-CN)
username is how you want to be identified in terms of translation.  At some point there may be an "official" or "community" version.

Then load the file into QtLinguist (Manual here: https://doc.qt.io/qt-6/qtlinguist-index.html) and start the translation work.
When you are ready to test your translation, go to File->Release or File->Release As to give it a new name and then turn it into a .qm file.
In HueForge go to Preferences->Language->Manage Languages to add your new .qm file to HueForge which will immediately allow you to select it in the
language menu, restart HueForge and be running with the new version.

Ideally this will be the central repository for HueForge translations, but I encourage translators to spread their files directly within their
communities as well to improve and refine translations before submitting them as pull requests.

From time to time, a new HueForge_en.ts will be released (as new text is added to the UI).  When this happens, you can use tools\ts_file_utility.py
to merge the update with your existing translation non-destructively (all previous translations will be left alone).  Check the README.md in the tools
folder for more information on how to use ts_file_utility.py
