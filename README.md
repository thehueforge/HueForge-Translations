# HueForge Translations

Welcome to the public repository for HueForge translation files! This repository serves as the central hub for adding and maintaining translations for the HueForge application.

## Overview

HueForge uses Qt's translation system with `.ts` files (XML format) for internationalization. These files contain all the translatable strings from the application interface.

## Getting Started

### 1. Get the Source Translation File

The main translation file is `HueForge_en.ts`, which contains the most recent set of untranslated English strings. This is your starting point for any new translation.

### 2. File Naming Convention

When creating a new translation, rename the source file using this format:

```
HueForge_[language_code]_[username].ts
```

**Examples:**
- `HueForge_ja_tanaka.ts` (Japanese by user "tanaka")
- `HueForge_es_rodriguez.ts` (Spanish by user "rodriguez") 
- `HueForge_zh-CN_community.ts` (Simplified Chinese by "community")
- `HueForge_es-MX_official.ts` (Mexican Spanish, official version)

**Where:**
- `language_code` = 2-character language code (or 4 characters for regional variants like `es-MX`, `zh-CN`)
- `username` = Your preferred identifier as a translator

> **Note:** Eventually there may be "official" or "community" versions for each language.

## Translation Tools

### Qt Linguist (Recommended)

Qt Linguist is the easiest and most powerful tool for working with `.ts` files.

**Getting Qt Linguist:**
- **Windows**: Download standalone executables from [Qt-Linguist repository](https://github.com/thurask/Qt-Linguist)
- **macOS/Linux**: Install via Qt Maintenance Tool (standalone versions coming soon)
- **Documentation**: [Qt Linguist Manual](https://doc.qt.io/qt-6/qtlinguist-index.html)

Qt also maintains [official localization files](https://doc.qt.io/qt-6/qtlinguist-index.html) for Qt Linguist itself.

### Alternative Tools

While Qt Linguist is recommended, you can also use:
- Any XML editor
- Text editors with XML syntax highlighting
- Other translation tools that support Qt's `.ts` format

## Translation Workflow

### 1. Create Your Translation File
```bash
# Copy the source file
cp HueForge_en.ts HueForge_ja_yourname.ts
```

### 2. Open in Qt Linguist
1. Launch Qt Linguist
2. Open your newly created `.ts` file
3. Begin translating strings

### 3. Test Your Translation
1. In Qt Linguist: **File → Release** or **File → Release As**
2. This creates a `.qm` file (compiled translation)
3. In HueForge: **Preferences → Language → Manage Languages**
4. Add your `.qm` file to HueForge
5. Select your language from the language menu
6. Restart HueForge to see your translation in action

## Updating Existing Translations

When new versions of `HueForge_en.ts` are released (containing new UI text), you can update your existing translation without losing your previous work.

### Using the Translation Utility

Use the provided `tools/ts_file_utility.py` script for non-destructive updates:

```bash
# Update your translation with new strings from the latest source
python tools/ts_file_utility.py update HueForge_en.ts HueForge_ja_yourname.ts ja
```

This command will:
- ✅ Preserve all your existing translations
- ✅ Add new untranslated strings from the updated source
- ✅ Create a backup of your current file
- ✅ Handle placeholder formatting automatically

For more information about the translation utility, see the [tools README](tools/README.md).

## Contributing

### Direct Community Distribution

We encourage translators to:
- Share translation files directly within their communities
- Gather feedback and refine translations
- Collaborate with other speakers of the same language

### Submitting to Repository

When your translation is ready for wider distribution:

1. **Fork** this repository
2. **Add** your translation file to the appropriate directory
3. **Submit** a pull request with:
   - Your translation file
   - Brief description of the translation
   - Any special notes or regional considerations

### Translation Quality

To ensure high-quality translations:
- Test your translation thoroughly in the HueForge application
- Consider context and UI space constraints
- Maintain consistency in terminology
- Follow your language's localization conventions

## File Structure

```
HueForge-Translations/
├── LICENSE                    # License file (CC BY-NC-SA 4.0)
├── README.md                 # This file
├── release files/            # Compiled translations (.qm) for use in HueForge
│   ├── Chinese - Simplified/
│   │   └── HueForge_zh_Evan76.qm
│   ├── French/
│   │   ├── HueForge_fr_Placeholder.qm
│   │   └── HueForge_fr_QuasarCreations3D.qm
│   └── Japanese/
│       ├── HueForge_ja_daisuke.qm
│       └── welcome_td_ja_daisuke.html
├── src/
│   ├── html/                 # Localized HTML content
│   │   ├── French/
│   │   │   └── welcome_td_fr_google.html
│   │   └── Japanese/
│   │       └── welcome_td_ja_daisuke.html
│   ├── json/                 # Reserved for future localization-related JSON
│   └── ts_files/             # Main translation sources (.ts files)
│       ├── HueForge_en.ts
│       ├── Chinese - Simplified/
│       │   └── HueForge_zh_Evan76.ts
│       ├── French/
│       │   ├── HueForge_fr_PlaceholderMixed.ts
│       │   ├── HueForge_fr_QuasarCreations3D.ts
│       │   └── HueForge_fr_QuasarCreations3DMixed.ts
│       └── Japanese/
├── tools/
│   ├── README.md             # Tool usage instructions
│   └── ts_file_utility.py    # Script for merging/updating .ts files
```

## Language Codes Reference

Common language codes for translation files:

| Language | Code | Example Filename |
|----------|------|------------------|
| Japanese | `ja` | `HueForge_ja_username.ts` |
| Spanish | `es` | `HueForge_es_username.ts` |
| Spanish (Mexico) | `es-MX` | `HueForge_es-MX_username.ts` |
| French | `fr` | `HueForge_fr_username.ts` |
| German | `de` | `HueForge_de_username.ts` |
| Chinese (Simplified) | `zh-CN` | `HueForge_zh-CN_username.ts` |
| Chinese (Traditional) | `zh-TW` | `HueForge_zh-TW_username.ts` |
| Korean | `ko` | `HueForge_ko_username.ts` |
| Russian | `ru` | `HueForge_ru_username.ts` |
| Portuguese | `pt` | `HueForge_pt_username.ts` |
| Italian | `it` | `HueForge_it_username.ts` |

## Support and Questions

- **Issues**: Use GitHub Issues for bug reports or feature requests
- **Discussions**: Use GitHub Discussions for general questions
- **Documentation**: Refer to the [Qt Linguist Manual](https://doc.qt.io/qt-6/qtlinguist-index.html)

## License

Translation files in this repository are licensed under **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

### What this means:

✅ **You can:**
- Use translations in any application (including commercial software like HueForge)
- Modify and improve translations
- Share translations with others
- Use translations for business/internal purposes

❌ **You cannot:**
- Sell translation files or charge money for providing them
- Create commercial translation services based on these files
- Use translations in ways that primarily generate revenue from the translations themselves

### Attribution Required
When using these translations, please provide appropriate credit to the HueForge translation community.

### Commercial Use Note
HueForge has separate rights to use these translations commercially. Other software projects may also incorporate these translations following the CC BY-NC-SA terms.

**Full License:** See [LICENSE](LICENSE) file or visit https://creativecommons.org/licenses/by-nc-sa/4.0/

---

**Happy translating!** Your contributions help make HueForge accessible to users worldwide. 🌍