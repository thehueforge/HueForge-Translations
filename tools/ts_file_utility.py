#!/usr/bin/env python3
"""
Qt Complete Translator
----------------------
A comprehensive tool for translating Qt TS files that handles:
1. Translation of TS files using Google Translate
2. Fixing common translation issues:
   - Proper handling of placeholders (%1, %2, %n)
   - Converting full-width symbols to half-width
   - Properly handling newlines and tabs
   - Preserving appropriate whitespace
3. Incremental updates - only translates entries missing in destination file
4. HTML file translation with proper tag and URL preservation

Usage:
python qt-complete-translator.py command input.ts output.ts [language]

Commands:
  translate   - Translate a TS, JSON, or HTML file to another language
  fix         - Fix formatting issues in an existing translation
  analyze     - Analyze placeholders in TS file without modifying
  compare     - Compare source and target TS files for differences
  update      - Update a translated TS file with new strings from source

Examples:
  python qt-complete-translator.py translate source.ts japanese.ts ja
  python qt-complete-translator.py fix japanese.ts japanese_fixed.ts
  python qt-complete-translator.py analyze japanese.ts
  python qt-complete-translator.py compare source.ts japanese.ts
  python qt-complete-translator.py update source.ts japanese.ts ja
  python qt-complete-translator.py translate index.html index_ja.html ja
"""

import sys
import re
import time
import os.path
import json
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from html.parser import HTMLParser
from html import escape, unescape

def analyze_placeholders(text):
    """
    Analyze a string to find placeholders and their surrounding whitespace.
    Returns a list of tuples (placeholder, pre_space, post_space)
    """
    results = []
    
    # Pattern to match Qt placeholders and surrounding whitespace
    pattern = re.compile(r'(\s*)(%\d+|\%n)(\s*)')
    
    for match in pattern.finditer(text):
        pre_space = match.group(1)
        placeholder = match.group(2)
        post_space = match.group(3)
        results.append((placeholder, pre_space, post_space))
    
    return results

def fix_translation_based_on_source(source_text, translation_text):
    """
    Fix translation text by comparing placeholder formatting with source text,
    while accounting for different language structures and placeholder positions.
    This function handles common translation issues with placeholders, newlines, tabs,
    and ampersands used for keyboard shortcuts.
    """
    if not source_text or not translation_text:
        return translation_text, False
    
    # Track if we've made modifications
    modified = False
    result = translation_text
    
    # First, check if all required placeholders are present in the translation
    source_placeholders = re.findall(r'%\d+|%n', source_text)
    trans_placeholders = re.findall(r'%\d+|%n', result)
    
    # Find missing placeholders
    missing_placeholders = set(source_placeholders) - set(trans_placeholders)
    if missing_placeholders and source_placeholders:
        # This is a serious issue - we need to try to add the missing placeholders
        print(f"Warning: Missing placeholders in translation: {missing_placeholders}")
        print(f"  Source: {source_text}")
        print(f"  Translation before fix: {result}")
        
        # For now, we'll just try to append the missing placeholders at the end
        # This is not perfect but better than having missing placeholders
        for placeholder in missing_placeholders:
            result += f" {placeholder}"
            modified = True
            
        print(f"  Translation after fix: {result}")
    
    # 1. Fix full-width percent symbols
    if '％' in result:
        result = result.replace('％', '%')
        modified = True
    
    # 2. Replace literal "newline_marker" with actual newlines (case insensitive)
    # Try different variations of newline marker text
    variations = [
        r'newline_marker',
        r'NEWLINE_MARKER',
        r'Newline_marker',
        r'Newline_Marker',
        r'NewLine_Marker'
    ]
    
    for variation in variations:
        if variation in result:
            result = result.replace(variation, '\n')
            modified = True
    
    # Also use regex for any other case variations
    newline_pattern = re.compile(r'newline_marker', re.IGNORECASE)
    if newline_pattern.search(result):
        result = newline_pattern.sub('\n', result)
        modified = True
    
    # 3. Fix placeholder_X_marker format 
    placeholder_pattern = re.compile(r'([Pp]lace[Hh]older_)(\d+)(_[Mm]arker)')
    if placeholder_pattern.search(result):
        for match in placeholder_pattern.finditer(result):
            num_str = match.group(2)
            placeholder_num = int(num_str) + 1  # Add 1 because placeholders are 1-indexed in Qt
            result = result.replace(match.group(0), f'%{placeholder_num}')
        modified = True
    
    # 4. Fix tab_marker to actual tabs
    if 'tab_marker' in result.lower():
        result = re.sub(r'(?i)tab_marker', '\t', result)
        modified = True
    
    # 5. Ensure placeholders are correctly formatted
    # This handles cases where placeholders might be in different positions
    # due to differences in language structure
    
    # Find all %n style placeholders in the result
    trans_placeholders = re.findall(r'%\d+|%n', result)
    
    # For each placeholder in the translation
    for placeholder in trans_placeholders:
        # Look for the pattern: placeholder immediately followed by non-whitespace
        pattern = re.compile(re.escape(placeholder) + r'(\S)')
        
        # Check if this placeholder in the source text has whitespace after it
        source_pattern = re.compile(re.escape(placeholder) + r'\s')
        
        # If the pattern exists in source and the placeholder in translation is missing space
        if source_pattern.search(source_text) and pattern.search(result):
            # Add a space after the placeholder in the translation
            result = pattern.sub(lambda m: placeholder + ' ' + m.group(1), result)
            modified = True
    
    # 6. Handle ampersands for keyboard shortcuts
    # Count ampersands in source (not counting double ampersands)
    source_ampersands = 0
    i = 0
    while i < len(source_text):
        if i < len(source_text) - 1 and source_text[i] == '&' and source_text[i+1] != '&':
            source_ampersands += 1
        i += 1
    
    # Count ampersands in result 
    result_ampersands = 0
    i = 0
    while i < len(result):
        if i < len(result) - 1 and result[i] == '&' and result[i+1] != '&':
            result_ampersands += 1
        i += 1
    
    # If source has ampersands but result doesn't, try to add them
    if source_ampersands > 0 and result_ampersands == 0:
        print(f"Warning: Missing keyboard shortcut in translation")
        print(f"  Source: {source_text}")
        print(f"  Translation before fix: {result}")
        
        # Find the first word and add an ampersand to its first letter
        match = re.search(r'\b([a-zA-Z0-9])[a-zA-Z0-9]*\b', result)
        if match:
            pos = match.start(1)
            result = result[:pos] + "&" + result[pos:]
            modified = True
            print(f"  Translation after fix: {result}")
    
    # 7. Fix multiple consecutive ampersands
    if '&&&' in result:
        # Three or more consecutive ampersands is likely a mistake
        result = re.sub(r'&{3,}', '&&', result)
        modified = True
    
    return result, modified

def translate_with_placeholder_preservation(source_text, target_language, translator):
    """
    Translate text while properly preserving placeholders
    """
    if not source_text:
        return source_text
    
    # Find all placeholders like %1, %2, etc. and escape them for translation
    # Also capture spaces around placeholders to preserve formatting
    placeholder_pattern = re.compile(r'(\s*)(%\d+|\%n)(\s*)')
    placeholders = []
    placeholder_map = {}
    
    # Create a modified text where placeholders are replaced with unique markers
    modified_text = source_text
    
    # Find all space-surrounded placeholders and replace them
    for match in placeholder_pattern.finditer(source_text):
        placeholder_with_space = match.group(0)
        placeholder = match.group(2)
        pre_space = match.group(1)
        post_space = match.group(3)
        
        # Use a unique marker that won't be changed by translation
        marker = f"PLACEHOLDER_{len(placeholders)}_MARKER"
        placeholder_map[marker] = {
            "placeholder": placeholder,
            "pre_space": pre_space,
            "post_space": post_space
        }
        placeholders.append(placeholder)
        modified_text = modified_text.replace(placeholder_with_space, marker)
    
    # Handle newlines and tabs specially
    special_markers = {}
    if '\n' in modified_text:
        modified_text = modified_text.replace('\n', ' NEWLINE_MARKER ')
        special_markers['NEWLINE_MARKER'] = '\n'
    if '\t' in modified_text:
        modified_text = modified_text.replace('\t', ' TAB_MARKER ')
        special_markers['TAB_MARKER'] = '\t'
    
    # Analyze whitespace patterns in the modified text
    leading_space = re.match(r'^(\s+)', modified_text)
    trailing_space = re.search(r'(\s+)$', modified_text)
    
    # Prepare the text for translation (trim whitespace)
    text_to_translate = modified_text.strip()
    
    if text_to_translate:  # Only translate non-empty strings
        # Translate the modified text
        translated_text = translator.translate(text_to_translate)
        
        # Restore leading and trailing whitespace
        if leading_space:
            translated_text = leading_space.group(1) + translated_text
        if trailing_space:
            translated_text = translated_text + trailing_space.group(1)
        
        # Restore newlines and tabs
        for marker, special_char in special_markers.items():
            translated_text = translated_text.replace(f' {marker} ', special_char)
            # Also try without spaces (in case the translator merged them)
            translated_text = translated_text.replace(marker, special_char)
        
        # Restore placeholders with their original spacing
        for marker, placeholder_info in placeholder_map.items():
            placeholder = placeholder_info["placeholder"]
            translated_text = translated_text.replace(marker, placeholder)
    else:
        # If the string is just whitespace, keep it as is
        translated_text = source_text
    
    return translated_text

class HTMLTranslator(HTMLParser):
    """
    HTML parser that translates text content while preserving tags and structure
    """
    
    def __init__(self, target_language, translator):
        super().__init__()
        self.target_language = target_language
        self.translator = translator
        self.result = []
        self.current_tag = None
        self.skip_translation = False
        self.translated_strings = 0
        self.total_strings = 0
        
        # Tags where we should not translate content
        self.skip_tags = {'script', 'style', 'code', 'pre', 'link', 'meta'}
        
        # Attributes that might contain translatable text
        self.translatable_attrs = {'title', 'alt', 'placeholder', 'aria-label', 'aria-describedby'}
    
    def should_translate_text(self, text):
        """
        Determine if a text string should be translated
        """
        if not text or not text.strip():
            return False
        
        # Skip URLs
        if re.match(r'^(https?:|www\.|ftp:|file:|mailto:)', text.strip()):
            return False
        
        # Skip email addresses
        if re.match(r'^[^@]+@[^@]+\.[^@]+$', text.strip()):
            return False
        
        # Skip file paths
        if re.match(r'^[./\\].*', text.strip()):
            return False
        
        # Skip strings that are just numbers, symbols, or whitespace
        if re.match(r'^[\d\W\s]+$', text.strip()):
            return False
        
        # Skip very short strings (single characters, etc.)
        if len(text.strip()) <= 1:
            return False
        
        return True
    
    def translate_text(self, text):
        """
        Translate a text string while preserving its structure
        """
        if not self.should_translate_text(text):
            return text
        
        self.total_strings += 1
        try:
            # Preserve leading and trailing whitespace
            leading_space = re.match(r'^(\s*)', text)
            trailing_space = re.search(r'(\s*)$', text)
            
            text_to_translate = text.strip()
            if text_to_translate:
                translated = translate_with_placeholder_preservation(
                    text_to_translate, self.target_language, self.translator)
                
                # Restore whitespace
                if leading_space:
                    translated = leading_space.group(1) + translated
                if trailing_space:
                    translated = translated + trailing_space.group(1)
                
                self.translated_strings += 1
                time.sleep(0.3)  # Small delay to avoid rate limiting
                return translated
            else:
                return text
        except Exception as e:
            print(f"Error translating text: {text[:50]}...")
            print(f"Error details: {e}")
            return text
    
    def handle_starttag(self, tag, attrs):
        """
        Handle opening HTML tags
        """
        self.current_tag = tag
        self.skip_translation = tag.lower() in self.skip_tags
        
        # Start building the tag
        tag_parts = [f'<{tag}']
        
        # Process attributes
        for attr_name, attr_value in attrs:
            if attr_value is None:
                tag_parts.append(f' {attr_name}')
            else:
                # Translate certain attributes if they contain user-facing text
                if (attr_name.lower() in self.translatable_attrs and 
                    self.should_translate_text(attr_value)):
                    
                    try:
                        translated_value = self.translate_text(attr_value)
                        tag_parts.append(f' {attr_name}="{escape(translated_value)}"')
                    except Exception as e:
                        print(f"Error translating attribute {attr_name}: {attr_value}")
                        tag_parts.append(f' {attr_name}="{escape(attr_value)}"')
                else:
                    # Don't translate this attribute
                    tag_parts.append(f' {attr_name}="{escape(attr_value)}"')
        
        tag_parts.append('>')
        self.result.append(''.join(tag_parts))
    
    def handle_endtag(self, tag):
        """
        Handle closing HTML tags
        """
        self.result.append(f'</{tag}>')
        self.current_tag = None
        self.skip_translation = False
    
    def handle_data(self, data):
        """
        Handle text content between tags
        """
        if self.skip_translation:
            # Don't translate content in script, style, etc.
            self.result.append(data)
        else:
            # Translate the text content
            translated_data = self.translate_text(data)
            self.result.append(translated_data)
    
    def handle_comment(self, data):
        """
        Handle HTML comments - preserve them as-is
        """
        self.result.append(f'<!--{data}-->')
    
    def handle_decl(self, decl):
        """
        Handle DOCTYPE declarations
        """
        self.result.append(f'<!{decl}>')
    
    def handle_charref(self, name):
        """
        Handle character references like &#123;
        """
        self.result.append(f'&#{name};')
    
    def handle_entityref(self, name):
        """
        Handle entity references like &amp;
        """
        self.result.append(f'&{name};')
    
    def get_result(self):
        """
        Get the translated HTML as a string
        """
        return ''.join(self.result)

def translate_html_file(input_file, output_file, target_language):
    """
    Translate an HTML file to the target language
    Preserves HTML structure while translating text content
    """
    try:
        # Read the HTML file
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Initialize translator
        translator = GoogleTranslator(source='auto', target=target_language)
        
        # Create HTML translator
        html_translator = HTMLTranslator(target_language, translator)
        
        print(f"Translating HTML file to {target_language}...")
        
        # Parse and translate the HTML
        html_translator.feed(html_content)
        translated_html = html_translator.get_result()
        
        # Check if output file exists
        if os.path.exists(output_file):
            print(f"Output file {output_file} exists. Creating backup...")
            backup_file = f"{output_file}.bak"
            import shutil
            shutil.copy2(output_file, backup_file)
        
        # Write the translated HTML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_html)
        
        print(f"Translation completed!")
        print(f"Total text strings processed: {html_translator.total_strings}")
        print(f"Strings translated: {html_translator.translated_strings}")
        print(f"Result saved to: {output_file}")
        
        return True
    except Exception as e:
        print(f"Error processing HTML file: {e}")
        return False

def update_html_file(source_file, target_file, target_language):
    """
    Update a translated HTML file with new content from source
    This is a simplified approach - HTML updates are complex due to structure changes
    For now, we'll just retranslate the entire file
    """
    print("Note: HTML update mode will retranslate the entire file.")
    print("For HTML files, it's recommended to use the 'translate' command instead.")
    return translate_html_file(source_file, target_file, target_language)

def load_existing_translations(file_path):
    """
    Load existing translations from a TS file into a dictionary for quick lookup
    Returns a dictionary with source text as key and translation object as value
    """
    translations = {}
    
    if not os.path.exists(file_path):
        return translations
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        for context in root.findall(".//context"):
            context_name = context.find("name").text if context.find("name") is not None else ""
            
            for message in context.findall("message"):
                source = message.find("source")
                if source is not None and source.text:
                    # Create a unique key using context name and source text
                    key = f"{context_name}|{source.text}"
                    
                    # Store the entire translation element
                    translation = message.find("translation")
                    if translation is not None:
                        translations[key] = translation
        
        return translations
    except Exception as e:
        print(f"Warning: Error loading existing translations: {e}")
        return {}

def translate_ts_file(input_file, output_file, target_language):
    """
    Translate a TS file to the target language with proper placeholder handling
    Only translates entries that don't exist in the output file
    Automatically fixes placeholder and newline issues during translation
    """
    try:
        # Check if output file exists and load existing translations
        existing_translations = {}
        if os.path.exists(output_file):
            print(f"Output file {output_file} exists. Loading existing translations...")
            existing_translations = load_existing_translations(output_file)
            print(f"Loaded {len(existing_translations)} existing translations")
            
            # Create a backup of the existing file
            backup_file = f"{output_file}.bak"
            print(f"Creating backup of existing file at {backup_file}")
            import shutil
            shutil.copy2(output_file, backup_file)
        
        # Parse TS file
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # Initialize translator
        translator = GoogleTranslator(source='auto', target=target_language)
        
        # Count total messages for progress reporting
        total_messages = len(root.findall(".//message"))
        processed = 0
        translated = 0
        skipped = 0
        
        # Process all contexts
        for context in root.findall(".//context"):
            context_name = context.find("name").text if context.find("name") is not None else ""
            
            # Process all messages in this context
            for message in context.findall("message"):
                source = message.find("source")
                if source is not None and source.text:
                    # Get the source text
                    source_text = source.text
                    
                    # Create a unique key for this message
                    key = f"{context_name}|{source_text}"
                    
                    # Check if this is a plural form message
                    is_plural = message.get("numerus") == "yes"
                    
                    # Get or create translation element
                    translation = message.find("translation")
                    if translation is None:
                        translation = ET.SubElement(message, "translation")
                        if is_plural:
                            translation.set("type", "unfinished")
                    
                    # Check if this message is already translated in the existing file
                    if key in existing_translations:
                        existing_translation = existing_translations[key]
                        
                        # Check if the existing translation is valid (not unfinished or empty)
                        is_valid = (existing_translation.get("type") != "unfinished" and 
                                  (existing_translation.text or existing_translation.findall("numerusform")))
                        
                        if is_valid:
                            # Copy the existing translation
                            if is_plural:
                                # Copy all numerusform elements
                                # First, remove any existing numerusform in the current translation
                                for numerus in translation.findall("numerusform"):
                                    translation.remove(numerus)
                                
                                # Then copy all numerusform elements from existing translation
                                for numerus in existing_translation.findall("numerusform"):
                                    new_numerus = ET.SubElement(translation, "numerusform")
                                    new_numerus.text = numerus.text
                            else:
                                # Regular translation
                                translation.text = existing_translation.text
                            
                            # Copy attributes but remove "unfinished" type
                            for attr, value in existing_translation.attrib.items():
                                if attr == "type" and value == "unfinished":
                                    continue
                                translation.set(attr, value)
                            
                            skipped += 1
                            processed += 1
                            continue
                    
                    # Skip if translation already exists and is not marked as unfinished
                    if translation.get("type") != "unfinished" and translation.text:
                        processed += 1
                        continue
                    
                    try:
                        # Translate the source text
                        translated_text = translate_with_placeholder_preservation(
                            source_text, target_language, translator)
                        
                        # Apply additional fixes to the translated text
                        fixed_text, modified = fix_translation_based_on_source(source_text, translated_text)
                        if modified:
                            print(f"Fixed placeholder issues in: {source_text}")
                            translated_text = fixed_text
                        
                        # Handle plural forms differently
                        if is_plural:
                            # Clear existing numerusform elements if any
                            for numerus in translation.findall("numerusform"):
                                translation.remove(numerus)
                            
                            # Create numerusform element(s)
                            numerus_form = ET.SubElement(translation, "numerusform")
                            numerus_form.text = translated_text
                            
                            # Add more forms for languages that need them
                            if target_language not in ["ja", "zh-CN", "zh-TW"]:
                                numerus_form2 = ET.SubElement(translation, "numerusform")
                                numerus_form2.text = translated_text
                        else:
                            # Regular translation
                            translation.text = translated_text
                        
                        # Remove the "unfinished" type
                        if "type" in translation.attrib:
                            translation.attrib.pop("type")
                        
                        translated += 1
                        
                        # Add a small delay to avoid rate limiting
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"Error translating: {source_text}")
                        print(f"Error details: {e}")
                        
                        # Mark as unfinished if there was an error
                        translation.set("type", "unfinished")
                
                processed += 1
                if processed % 10 == 0:
                    percent = int(processed / total_messages * 100)
                    print(f"Processed {processed}/{total_messages} strings ({percent}%)")
        
        # Write the result to the output file
        tree.write(output_file, encoding="UTF-8", xml_declaration=True)
        
        print(f"Translation completed!")
        print(f"Processed {processed} messages")
        print(f"Translated {translated} messages")
        print(f"Skipped {skipped} already translated messages")
        print(f"Result saved to: {output_file}")
        
        return True
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

def fix_ts_file(input_file, output_file):
    """Process a TS file and fix common translation issues"""
    try:
        # Parse TS file
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # Track statistics
        total_translations = 0
        fixed_translations = 0
        
        # Process all message elements
        for message in root.findall(".//message"):
            # Get the source text
            source = message.find("source")
            source_text = source.text if source is not None and source.text else ""
            
            # Get the translation element
            translation = message.find("translation")
            if translation is not None:
                # Fix direct translation text
                if translation.text:
                    total_translations += 1
                    fixed_text, modified = fix_translation_based_on_source(source_text, translation.text)
                    if modified:
                        translation.text = fixed_text
                        fixed_translations += 1
                
                # Fix text in numerusform elements (for plural forms)
                for numerus in translation.findall("numerusform"):
                    if numerus.text:
                        total_translations += 1
                        fixed_text, modified = fix_translation_based_on_source(source_text, numerus.text)
                        if modified:
                            numerus.text = fixed_text
                            fixed_translations += 1
        
        # Write the fixed file
        tree.write(output_file, encoding="UTF-8", xml_declaration=True)
        
        print(f"Processing complete!")
        print(f"Examined {total_translations} translations")
        print(f"Fixed {fixed_translations} translations")
        print(f"Fixed file saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

def analyze_ts_file(input_file):
    """
    Analyze a TS file for placeholder patterns and potential issues
    including ampersand keyboard shortcuts
    """
    try:
        # Parse TS file
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        print("Analyzing TS file for placeholder patterns and keyboard shortcuts...\n")
        
        # Track statistics
        total_messages = 0
        messages_with_placeholders = 0
        messages_with_shortcuts = 0
        potential_issues = 0
        
        # Process all messages
        for message in root.findall(".//message"):
            total_messages += 1
            
            # Get the source and translation
            source = message.find("source")
            translation = message.find("translation")
            
            source_text = source.text if source is not None and source.text else ""
            translation_text = ""
            
            if translation is not None:
                # Check direct translation text or numerusform
                if translation.text:
                    translation_text = translation.text
                elif translation.findall("numerusform"):
                    # Use the first numerusform for analysis
                    numerus = translation.find("numerusform")
                    if numerus is not None and numerus.text:
                        translation_text = numerus.text
            
            # Find placeholders in source and translation
            source_placeholders = re.findall(r'%\d+|%n', source_text)
            translation_placeholders = re.findall(r'%\d+|%n', translation_text)
            
            # Count ampersands in source (for keyboard shortcuts)
            source_shortcut_count = 0
            i = 0
            while i < len(source_text):
                if source_text[i] == '&':
                    if i + 1 < len(source_text) and source_text[i+1] != '&':  # Not a double ampersand
                        source_shortcut_count += 1
                    i += 2  # Skip the character after the ampersand
                else:
                    i += 1
            
            # Count ampersands in translation
            translation_shortcut_count = 0
            i = 0
            while i < len(translation_text):
                if translation_text[i] == '&':
                    if i + 1 < len(translation_text) and translation_text[i+1] != '&':  # Not a double ampersand
                        translation_shortcut_count += 1
                    i += 2  # Skip the character after the ampersand
                else:
                    i += 1
            
            # Check for potential issues
            has_issue = False
            
            if source_placeholders:
                messages_with_placeholders += 1
                
                # 1. Check if all source placeholders are in translation
                missing_placeholders = set(source_placeholders) - set(translation_placeholders)
                if missing_placeholders:
                    has_issue = True
                
                # 2. Check for placeholder format issues
                if '％' in translation_text:  # Full-width percent
                    has_issue = True
                
                # 3. Check for placeholder spacing issues
                for placeholder in translation_placeholders:
                    # Look for placeholder immediately followed by non-whitespace
                    if re.search(re.escape(placeholder) + r'\S', translation_text):
                        # Check if this placeholder has space after it in source
                        if re.search(re.escape(placeholder) + r'\s', source_text):
                            has_issue = True
                
                # 4. Check for literal markers
                if 'newline_marker' in translation_text.lower() or 'placeholder' in translation_text.lower():
                    has_issue = True
                
                # 5. Check for extra placeholders in translation
                extra_placeholders = set(translation_placeholders) - set(source_placeholders)
                if extra_placeholders:
                    has_issue = True
            
            # Check for shortcut issues
            if source_shortcut_count > 0:
                messages_with_shortcuts += 1
                
                # 1. Check if shortcuts are missing in translation
                if source_shortcut_count > 0 and translation_shortcut_count == 0:
                    has_issue = True
                
                # 2. Check for excessive shortcuts in translation
                if translation_shortcut_count > source_shortcut_count + 1:  # Allow for one extra
                    has_issue = True
                
                # 3. Check for consecutive ampersands (which might be errors)
                if '&&&' in translation_text:
                    has_issue = True
            
            if has_issue:
                potential_issues += 1
                print(f"Potential issue found in message:")
                print(f"  Source: {source_text}")
                print(f"  Translation: {translation_text}")
                
                if source_placeholders:
                    print(f"  Source placeholders: {source_placeholders}")
                    print(f"  Translation placeholders: {translation_placeholders}")
                
                if source_shortcut_count > 0:
                    print(f"  Source shortcut count: {source_shortcut_count}")
                    print(f"  Translation shortcut count: {translation_shortcut_count}")
                
                print()
        
        # Print summary
        print("\nAnalysis Summary:")
        print(f"Total messages: {total_messages}")
        print(f"Messages with placeholders: {messages_with_placeholders}")
        print(f"Messages with keyboard shortcuts: {messages_with_shortcuts}")
        print(f"Messages with potential issues: {potential_issues}")
        
        return True
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return False
                
def compare_ts_files(source_file, target_file):
    """
    Compare source and target TS files to identify differences
    Returns statistics about missing/added/changed translations
    """
    try:
        if not os.path.exists(target_file):
            print(f"Target file {target_file} does not exist. Nothing to compare.")
            return False
        
        # Parse source and target files
        source_tree = ET.parse(source_file)
        source_root = source_tree.getroot()
        
        target_tree = ET.parse(target_file)
        target_root = target_tree.getroot()
        
        # Build dictionaries for quick lookup
        source_messages = {}
        target_messages = {}
        
        # Process source file
        for context in source_root.findall(".//context"):
            context_name = context.find("name").text if context.find("name") is not None else ""
            
            for message in context.findall("message"):
                source_elem = message.find("source")
                if source_elem is not None and source_elem.text:
                    key = f"{context_name}|{source_elem.text}"
                    source_messages[key] = message
        
        # Process target file
        for context in target_root.findall(".//context"):
            context_name = context.find("name").text if context.find("name") is not None else ""
            
            for message in context.findall("message"):
                source_elem = message.find("source")
                if source_elem is not None and source_elem.text:
                    key = f"{context_name}|{source_elem.text}"
                    target_messages[key] = message
        
        # Calculate statistics
        source_count = len(source_messages)
        target_count = len(target_messages)
        
        # Messages in source but not in target
        missing_messages = set(source_messages.keys()) - set(target_messages.keys())
        
        # Messages in target but not in source
        extra_messages = set(target_messages.keys()) - set(source_messages.keys())
        
        # Messages in both but with different translations
        changed_messages = 0
        for key in set(source_messages.keys()) & set(target_messages.keys()):
            source_message = source_messages[key]
            target_message = target_messages[key]
            
            source_translation = source_message.find("translation")
            target_translation = target_message.find("translation")
            
            # Skip if either translation is missing
            if source_translation is None or target_translation is None:
                continue
            
            # Check for differences in text content
            if source_translation.text != target_translation.text:
                changed_messages += 1
        
        # Print results
        print("\nComparison Summary:")
        print(f"Source file messages: {source_count}")
        print(f"Target file messages: {target_count}")
        print(f"Messages missing in target: {len(missing_messages)}")
        print(f"Extra messages in target: {len(extra_messages)}")
        print(f"Messages with different translations: {changed_messages}")
        
        return True
    except Exception as e:
        print(f"Error comparing files: {e}")
        return False

def update_ts_file(source_file, target_file, target_language):
    """
    Update a translated TS file with new strings from source
    Only translates entries that are in source but not in target
    NEVER replaces existing translations, regardless of completion status
    """
    try:
        # Check if target file exists
        if not os.path.exists(target_file):
            print(f"Target file {target_file} does not exist. Will create a new file.")
            return translate_ts_file(source_file, target_file, target_language)
        
        # Load existing translations from target
        existing_translations = load_existing_translations(target_file)
        print(f"Loaded {len(existing_translations)} existing translations from {target_file}")
        
        # Create a backup of the target file
        backup_file = f"{target_file}.bak"
        print(f"Creating backup of existing file at {backup_file}")
        import shutil
        shutil.copy2(target_file, backup_file)
        
        # Parse source and target files
        source_tree = ET.parse(source_file)
        source_root = source_tree.getroot()
        
        target_tree = ET.parse(target_file)
        target_root = target_tree.getroot()
        
        # Initialize translator
        translator = GoogleTranslator(source='auto', target=target_language)
        
        # Track statistics
        total_messages = 0
        added_messages = 0
        skipped_existing = 0
        
        # Process each context in source
        for source_context in source_root.findall(".//context"):
            context_name = source_context.find("name").text if source_context.find("name") is not None else ""
            
            # Try to find matching context in target
            target_context = None
            for tc in target_root.findall(".//context"):
                tc_name = tc.find("name").text if tc.find("name") is not None else ""
                if tc_name == context_name:
                    target_context = tc
                    break
            
            # If context doesn't exist in target, create it
            if target_context is None:
                print(f"Adding new context: {context_name}")
                target_context = ET.SubElement(target_root, "context")
                name_elem = ET.SubElement(target_context, "name")
                name_elem.text = context_name
            
            # Process each message in this context
            for source_message in source_context.findall("message"):
                total_messages += 1
                
                source_elem = source_message.find("source")
                if source_elem is not None and source_elem.text:
                    # Get the source text
                    source_text = source_elem.text
                    
                    # Create a unique key for this message
                    key = f"{context_name}|{source_text}"
                    
                    # Check if message exists in target context
                    found_in_target = False
                    target_message = None
                    
                    for tm in target_context.findall("message"):
                        tm_source = tm.find("source")
                        if tm_source is not None and tm_source.text == source_text:
                            found_in_target = True
                            target_message = tm
                            break
                    
                    # If message doesn't exist in target, add it
                    if not found_in_target:
                        print(f"Adding new message: {source_text[:40]}...")
                        target_message = ET.SubElement(target_context, "message")
                        
                        # Copy attributes from source message
                        for attr, value in source_message.attrib.items():
                            target_message.set(attr, value)
                        
                        # Create source element
                        new_source = ET.SubElement(target_message, "source")
                        new_source.text = source_text
                        
                        # Check if this is a plural form message
                        is_plural = source_message.get("numerus") == "yes"
                        
                        # Create translation element
                        new_translation = ET.SubElement(target_message, "translation")
                        if is_plural:
                            new_translation.set("type", "unfinished")
                        
                        # Translate the source text
                        translated_text = translate_with_placeholder_preservation(
                            source_text, target_language, translator)
                        
                        # Apply fixes to the translated text
                        fixed_text, modified = fix_translation_based_on_source(source_text, translated_text)
                        if modified:
                            translated_text = fixed_text
                        
                        # Handle plural forms
                        if is_plural:
                            # Create numerusform element(s)
                            numerus_form = ET.SubElement(new_translation, "numerusform")
                            numerus_form.text = translated_text
                            
                            # Add more forms for languages that need them
                            if target_language not in ["ja", "zh-CN", "zh-TW"]:
                                numerus_form2 = ET.SubElement(new_translation, "numerusform")
                                numerus_form2.text = translated_text
                        else:
                            # Regular translation
                            new_translation.text = translated_text
                        
                        added_messages += 1
                        time.sleep(0.5)  # Small delay to avoid rate limiting
                    
                    # If message exists, skip it completely (preserve existing translation)
                    else:
                        skipped_existing += 1
                        # Optionally log what we're skipping
                        if skipped_existing <= 5:  # Only show first few to avoid spam
                            print(f"Skipping existing message: {source_text[:40]}...")
        
        # Write the updated file
        target_tree.write(target_file, encoding="UTF-8", xml_declaration=True)
        
        print(f"Update completed!")
        print(f"Processed {total_messages} messages from source")
        print(f"Added {added_messages} new messages")
        print(f"Skipped {skipped_existing} existing messages (preserved)")
        print(f"Result saved to: {target_file}")
        
        return True
    except Exception as e:
        print(f"Error updating file: {e}")
        return False

def translate_json_file(input_file, output_file, target_language):
    """
    Translate a JSON file to the target language
    Preserves the JSON structure while translating string values
    """
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Initialize translator
        translator = GoogleTranslator(source='auto', target=target_language)
        
        # Translated output
        translated_data = {}
        
        # Track statistics
        total_strings = 0
        translated_strings = 0
        
        # Function to recursively translate strings in nested JSON
        def translate_json_value(value):
            nonlocal total_strings, translated_strings
            
            if isinstance(value, str):
                # Skip URLs, email addresses, file paths, and other non-translatable strings
                if re.match(r'^(https?:|www\.|file:|mailto:|/|\\|[^@]+@[^@]+\.[^@]+).*', value.strip()):
                    return value
                
                # Skip empty strings
                if not value.strip():
                    return value
                
                # Skip strings that are just numbers or symbols
                if re.match(r'^[\d\W]+', value.strip()):
                    return value
                
                total_strings += 1
                try:
                    # Translate the string, preserving placeholders, ampersands, etc.
                    translated = translate_with_placeholder_preservation(value, target_language, translator)
                    translated_strings += 1
                    
                    # Add small delay to avoid rate limiting
                    time.sleep(0.5)
                    
                    return translated
                except Exception as e:
                    print(f"Error translating: {value}")
                    print(f"Error details: {e}")
                    return value
            elif isinstance(value, dict):
                return {k: translate_json_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [translate_json_value(item) for item in value]
            else:
                return value
        
        # Translate all values in the JSON
        print(f"Translating JSON file to {target_language}...")
        translated_data = translate_json_value(data)
        
        # Check if output file exists
        if os.path.exists(output_file):
            print(f"Output file {output_file} exists. Creating backup...")
            backup_file = f"{output_file}.bak"
            import shutil
            shutil.copy2(output_file, backup_file)
        
        # Write the translated JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=4)
        
        print(f"Translation completed!")
        print(f"Total strings processed: {total_strings}")
        print(f"Strings translated: {translated_strings}")
        print(f"Result saved to: {output_file}")
        
        return True
    except Exception as e:
        print(f"Error processing JSON file: {e}")
        return False

def update_json_file(source_file, target_file, target_language):
    """
    Update a translated JSON file with new strings from source
    Only translates keys that are in source but not in target
    NEVER replaces existing translations, regardless of their content
    """
    try:
        # Check if target file exists
        if not os.path.exists(target_file):
            print(f"Target file {target_file} does not exist. Will create a new file.")
            return translate_json_file(source_file, target_file, target_language)
        
        # Read source and target JSON files
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        with open(target_file, 'r', encoding='utf-8') as f:
            target_data = json.load(f)
        
        # Create a backup of the target file
        backup_file = f"{target_file}.bak"
        print(f"Creating backup of existing file at {backup_file}")
        import shutil
        shutil.copy2(target_file, backup_file)
        
        # Initialize translator
        translator = GoogleTranslator(source='auto', target=target_language)
        
        # Track statistics
        added_strings = 0
        preserved_strings = 0
        
        # Function to recursively merge and translate missing strings
        def merge_json_objects(source, target, path=""):
            nonlocal added_strings, preserved_strings
            
            if isinstance(source, dict) and isinstance(target, dict):
                # New dictionary to hold updated result
                result = target.copy()
                
                # Process each key in source
                for key, source_value in source.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if key not in target:
                        # Key not in target, add it with translated value
                        if isinstance(source_value, str):
                            # Skip URLs, email addresses, and other non-translatable strings
                            if re.match(r'^(https?:|www\.|file:|mailto:|/|\\|[^@]+@[^@]+\.[^@]+).*', source_value.strip()):
                                result[key] = source_value
                            # Skip empty strings
                            elif not source_value.strip():
                                result[key] = source_value
                            # Skip strings that are just numbers or symbols
                            elif re.match(r'^[\d\W]+', source_value.strip()):
                                result[key] = source_value
                            else:
                                try:
                                    # Translate the string
                                    translated = translate_with_placeholder_preservation(source_value, target_language, translator)
                                    result[key] = translated
                                    added_strings += 1
                                    print(f"Added new string at {current_path}: {source_value[:30]}...")
                                    time.sleep(0.5)  # Delay to avoid rate limiting
                                except Exception as e:
                                    print(f"Error translating: {source_value}")
                                    print(f"Error details: {e}")
                                    result[key] = source_value
                        else:
                            # For non-string values, recursively process
                            result[key] = merge_json_objects(source_value, {}, current_path)
                    else:
                        # Key exists in target - preserve existing translation completely
                        target_value = target[key]
                        
                        if isinstance(source_value, dict) and isinstance(target_value, dict):
                            # Both are dictionaries, recursively merge (but still preserve existing strings)
                            result[key] = merge_json_objects(source_value, target_value, current_path)
                        elif isinstance(source_value, list) and isinstance(target_value, list):
                            # Both are lists
                            # If source list is longer, process additional items only
                            if len(source_value) > len(target_value):
                                # Copy existing items (preserve all existing translations)
                                new_list = target_value.copy()
                                
                                # Process additional items only
                                for i, item in enumerate(source_value[len(target_value):], start=len(target_value)):
                                    list_path = f"{current_path}[{i}]"
                                    
                                    if isinstance(item, str):
                                        # Skip URLs and other non-translatable strings
                                        if re.match(r'^(https?:|www\.|file:|mailto:|/|\\|[^@]+@[^@]+\.[^@]+).*', item.strip()):
                                            new_list.append(item)
                                        # Skip empty strings
                                        elif not item.strip():
                                            new_list.append(item)
                                        # Skip strings that are just numbers or symbols
                                        elif re.match(r'^[\d\W]+', item.strip()):
                                            new_list.append(item)
                                        else:
                                            try:
                                                # Translate the string
                                                translated = translate_with_placeholder_preservation(item, target_language, translator)
                                                new_list.append(translated)
                                                added_strings += 1
                                                print(f"Added new string at {list_path}: {item[:30]}...")
                                                time.sleep(0.5)  # Delay to avoid rate limiting
                                            except Exception as e:
                                                print(f"Error translating: {item}")
                                                print(f"Error details: {e}")
                                                new_list.append(item)
                                    else:
                                        # For non-string values, recursively process
                                        new_list.append(merge_json_objects(item, {}, list_path))
                                
                                result[key] = new_list
                            else:
                                # Target list is same length or longer - preserve it completely
                                result[key] = target_value
                                if isinstance(target_value, list) and len(target_value) > 0:
                                    preserved_strings += len([item for item in target_value if isinstance(item, str)])
                        else:
                            # Different types or string values - preserve target completely
                            result[key] = target_value
                            if isinstance(target_value, str) and target_value.strip():
                                preserved_strings += 1
                                # Optionally log what we're preserving (limit to avoid spam)
                                if preserved_strings <= 5:
                                    print(f"Preserving existing translation at {current_path}: {target_value[:30]}...")
                
                return result
            elif isinstance(source, list) and isinstance(target, list):
                # If the source list is longer, process additional items only
                if len(source) > len(target):
                    result = target.copy()  # Preserve all existing items
                    
                    # Process additional items only
                    for i, item in enumerate(source[len(target):], start=len(target)):
                        list_path = f"{path}[{i}]"
                        
                        if isinstance(item, str):
                            # Skip URLs and other non-translatable strings
                            if re.match(r'^(https?:|www\.|file:|mailto:|/|\\|[^@]+@[^@]+\.[^@]+).*', item.strip()):
                                result.append(item)
                            # Skip empty strings
                            elif not item.strip():
                                result.append(item)
                            # Skip strings that are just numbers or symbols
                            elif re.match(r'^[\d\W]+', item.strip()):
                                result.append(item)
                            else:
                                try:
                                    # Translate the string
                                    translated = translate_with_placeholder_preservation(item, target_language, translator)
                                    result.append(translated)
                                    added_strings += 1
                                    print(f"Added new string at {list_path}: {item[:30]}...")
                                    time.sleep(0.5)  # Delay to avoid rate limiting
                                except Exception as e:
                                    print(f"Error translating: {item}")
                                    print(f"Error details: {e}")
                                    result.append(item)
                        else:
                            # For non-string values, recursively process
                            result.append(merge_json_objects(item, {}, list_path))
                    
                    return result
                else:
                    # Target list is same length or longer - preserve it completely
                    if isinstance(target, list) and len(target) > 0:
                        preserved_strings += len([item for item in target if isinstance(item, str)])
                    return target
            elif isinstance(source, str) and isinstance(target, str):
                # Both are strings, always preserve the target (existing translation)
                preserved_strings += 1
                return target
            else:
                # Different types or non-container types, preserve target if it exists
                if target is not None:
                    if isinstance(target, str) and target.strip():
                        preserved_strings += 1
                    return target
                else:
                    return source
        
        # Merge source into target, translating new strings only
        updated_data = merge_json_objects(source_data, target_data)
        
        # Write the updated JSON
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)
        
        print(f"Update completed!")
        print(f"Added {added_strings} new strings")
        print(f"Preserved {preserved_strings} existing translations")
        print(f"Result saved to: {target_file}")
        
        return True
    except Exception as e:
        print(f"Error updating JSON file: {e}")
        return False

def print_help():
    """
    Print usage instructions
    """
    print("\nQt Complete Translator")
    print("----------------------")
    print("Usage: python qt-complete-translator.py command input_file output_file [language]")
    print("\nCommands:")
    print("  translate   - Translate a TS, JSON, or HTML file to another language")
    print("  fix         - Fix formatting issues in an existing translation")
    print("  analyze     - Analyze placeholders in TS file without modifying")
    print("  compare     - Compare source and target TS files to show differences")
    print("  update      - Update a translated file with new strings from source")
    print("\nExamples:")
    print("  python qt-complete-translator.py translate source.ts japanese.ts ja")
    print("  python qt-complete-translator.py fix japanese.ts japanese_fixed.ts")
    print("  python qt-complete-translator.py analyze japanese.ts")
    print("  python qt-complete-translator.py compare source.ts japanese.ts")
    print("  python qt-complete-translator.py update source.ts japanese.ts ja")
    print("  python qt-complete-translator.py translate help_videos.json help_videos_ja.json ja")
    print("  python qt-complete-translator.py translate index.html index_ja.html ja")

if __name__ == "__main__":
    # Check if enough arguments
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "translate":
        # Check arguments for translate
        if len(sys.argv) < 5:
            print("Error: translate command requires input file, output file, and target language")
            print_help()
            sys.exit(1)
        
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        target_language = sys.argv[4]
        
        # Check file extension to determine file type
        if input_file.lower().endswith('.json'):
            print(f"Detected JSON file. Translating {input_file} to {target_language}...")
            if translate_json_file(input_file, output_file, target_language):
                print("Translation completed successfully!")
            else:
                print("Translation failed.")
                sys.exit(1)
        elif input_file.lower().endswith('.ts'):
            print(f"Detected TS file. Translating {input_file} to {target_language}...")
            if translate_ts_file(input_file, output_file, target_language):
                print("Translation completed successfully!")
            else:
                print("Translation failed.")
                sys.exit(1)
        elif input_file.lower().endswith(('.html', '.htm')):
            print(f"Detected HTML file. Translating {input_file} to {target_language}...")
            if translate_html_file(input_file, output_file, target_language):
                print("Translation completed successfully!")
            else:
                print("Translation failed.")
                sys.exit(1)
        else:
            print(f"Error: Unsupported file type. Only .ts, .json, .html, and .htm files are supported.")
            print_help()
            sys.exit(1)
    
    elif command == "fix":
        # Check arguments for fix
        if len(sys.argv) < 4:
            print("Error: fix command requires input file and output file")
            print_help()
            sys.exit(1)
        
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        
        # Only TS files support the fix command
        if not input_file.lower().endswith('.ts'):
            print("Error: fix command only supports TS files")
            sys.exit(1)
        
        print(f"Fixing translation issues in {input_file}...")
        if fix_ts_file(input_file, output_file):
            print("Fixing completed successfully!")
        else:
            print("Fixing failed.")
            sys.exit(1)
    
    elif command == "analyze":
        # Check arguments for analyze
        if len(sys.argv) < 3:
            print("Error: analyze command requires input file")
            print_help()
            sys.exit(1)
        
        input_file = sys.argv[2]
        
        # Only TS files support the analyze command
        if not input_file.lower().endswith('.ts'):
            print("Error: analyze command only supports TS files")
            sys.exit(1)
        
        print(f"Analyzing {input_file}...")
        if analyze_ts_file(input_file):
            print("Analysis completed successfully!")
        else:
            print("Analysis failed.")
            sys.exit(1)
    
    elif command == "compare":
        # Check arguments for compare
        if len(sys.argv) < 4:
            print("Error: compare command requires source and target files")
            print_help()
            sys.exit(1)
        
        source_file = sys.argv[2]
        target_file = sys.argv[3]
        
        # Only TS files support the compare command
        if not source_file.lower().endswith('.ts') or not target_file.lower().endswith('.ts'):
            print("Error: compare command only supports TS files")
            sys.exit(1)
        
        print(f"Comparing {source_file} with {target_file}...")
        if compare_ts_files(source_file, target_file):
            print("Comparison completed successfully!")
        else:
            print("Comparison failed.")
            sys.exit(1)
    
    elif command == "update":
        # Check arguments for update
        if len(sys.argv) < 5:
            print("Error: update command requires source file, target file, and target language")
            print_help()
            sys.exit(1)
        
        source_file = sys.argv[2]
        target_file = sys.argv[3]
        target_language = sys.argv[4]
        
        # Check file extension to determine file type
        if source_file.lower().endswith('.json'):
            print(f"Detected JSON file. Updating {target_file} with new strings from {source_file}...")
            if update_json_file(source_file, target_file, target_language):
                print("Update completed successfully!")
            else:
                print("Update failed.")
                sys.exit(1)
        else:
            if update_ts_file(source_file, target_file, target_language):
                print("Update completed successfully!")
            else:
                print("Update failed.")
                sys.exit(1)