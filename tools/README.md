# Qt Complete Translator

A comprehensive Python tool for translating Qt TS files, JSON files, and HTML files with intelligent placeholder preservation, formatting fixes, and incremental updates.

## Features

- **Multi-format Support**: Translates Qt TS files, JSON files, and HTML files
- **Smart Placeholder Handling**: Properly preserves Qt placeholders (%1, %2, %n) during translation
- **Incremental Updates**: Only translates new or missing entries, preserving existing translations
- **Automatic Formatting Fixes**: Corrects common translation issues like full-width symbols, newline markers, and spacing
- **Keyboard Shortcut Preservation**: Maintains ampersand-based keyboard shortcuts (&File, &Edit, etc.)
- **HTML Structure Preservation**: Translates HTML content while maintaining tags, attributes, and structure
- **Comprehensive Analysis Tools**: Analyze files for potential translation issues
- **Backup Creation**: Automatically creates backups before modifying existing files

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/qt-complete-translator.git
cd qt-complete-translator
```

2. Install required dependencies:
```bash
pip install deep-translator
```

## Usage

### Basic Syntax
```bash
python ts_file_utility.py COMMAND INPUT_FILE OUTPUT_FILE [LANGUAGE]
```

### Commands

#### 1. Translate Files
Translate TS, JSON, or HTML files to another language:

```bash
# Translate Qt TS file
python ts_file_utility.py translate source.ts japanese.ts ja

# Translate JSON file
python ts_file_utility.py translate config.json config_ja.json ja

# Translate HTML file
python ts_file_utility.py translate index.html index_ja.html ja
```

#### 2. Fix Translation Issues
Fix formatting problems in existing TS translations:

```bash
python ts_file_utility.py fix japanese.ts japanese_fixed.ts
```

#### 3. Analyze Files
Analyze TS files for placeholder patterns and potential issues:

```bash
python ts_file_utility.py analyze japanese.ts
```

#### 4. Compare Files
Compare source and target TS files to identify differences:

```bash
python ts_file_utility.py compare source.ts japanese.ts
```

#### 5. Update Existing Translations
Add new strings from source to existing translated files (preserves all existing translations):

```bash
# Update TS file
python ts_file_utility.py update source.ts japanese.ts ja

# Update JSON file
python ts_file_utility.py update source.json target_ja.json ja
```

## Supported Languages

The tool supports all language codes compatible with Google Translate, including:

- `ja` - Japanese
- `zh-CN` - Chinese (Simplified)
- `zh-TW` - Chinese (Traditional)
- `ko` - Korean
- `es` - Spanish
- `fr` - French
- `de` - German
- `ru` - Russian
- `pt` - Portuguese
- `it` - Italian
- And many more...

## Translation Features

### Qt TS File Support
- **Placeholder Preservation**: Maintains Qt placeholders like `%1`, `%2`, `%n`
- **Plural Form Handling**: Properly handles `numerus="yes"` messages
- **Context Preservation**: Maintains Qt context structure
- **Incremental Updates**: Only translates missing entries

### JSON File Support
- **Nested Structure**: Handles deeply nested JSON objects and arrays
- **Selective Translation**: Skips URLs, email addresses, and file paths
- **Key Preservation**: Maintains JSON key structure
- **Array Handling**: Properly processes string arrays

### HTML File Support
- **Tag Preservation**: Maintains all HTML tags and structure
- **Attribute Translation**: Translates user-facing attributes like `title`, `alt`, `placeholder`
- **Content Filtering**: Skips `<script>`, `<style>`, and other non-translatable content
- **URL Protection**: Preserves links and file references

## Common Translation Issues Fixed

The tool automatically fixes these common problems:

1. **Full-width Symbols**: Converts `％` to `%` in placeholders
2. **Newline Markers**: Replaces `newline_marker` with actual newlines
3. **Placeholder Markers**: Converts `placeholder_X_marker` to `%X`
4. **Tab Markers**: Replaces `tab_marker` with actual tabs
5. **Spacing Issues**: Fixes placeholder spacing based on source text
6. **Missing Shortcuts**: Adds keyboard shortcuts when missing
7. **Consecutive Ampersands**: Fixes multiple `&&&` to `&&`

## Examples

### Basic Translation
```bash
# Translate a Qt TS file to Japanese
python ts_file_utility.py translate app.ts app_ja.ts ja
```

### Incremental Updates
```bash
# Add new strings from updated source to existing translation
python ts_file_utility.py update app_v2.ts app_ja.ts ja
```

### Fix Existing Translation
```bash
# Fix formatting issues in an existing translation
python ts_file_utility.py fix app_ja_broken.ts app_ja_fixed.ts
```

### Analysis and Comparison
```bash
# Analyze translation for issues
python ts_file_utility.py analyze app_ja.ts

# Compare source and translation
python ts_file_utility.py compare app.ts app_ja.ts
```

## File Backup

The tool automatically creates backup files (`.bak`) when modifying existing files, ensuring your original translations are never lost.

## Rate Limiting

Built-in delays prevent API rate limiting when using Google Translate, ensuring reliable translation of large files.

## Error Handling

- Graceful handling of translation API errors
- Preservation of original text when translation fails
- Detailed error reporting for troubleshooting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Dependencies

- `deep-translator` - For Google Translate integration
- Python 3.6+ - Required Python version

## Troubleshooting

### Common Issues

1. **Translation API Errors**: Ensure you have a stable internet connection
2. **File Encoding**: Make sure input files are UTF-8 encoded
3. **Large Files**: For very large files, consider breaking them into smaller chunks
4. **Rate Limiting**: The tool includes built-in delays, but very large files may need additional time

### Getting Help

If you encounter issues:
1. Check that your input file is valid (XML for TS, JSON for JSON files)
2. Ensure the target language code is supported by Google Translate
3. Verify you have write permissions for the output directory
4. Check the console output for specific error messages

## Changelog

### Version 1.0.0
- Initial release with TS, JSON, and HTML support
- Comprehensive placeholder preservation
- Incremental update functionality
- Analysis and comparison tools