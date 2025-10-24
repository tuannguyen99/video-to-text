#!/usr/bin/env python3
"""
Auto Google Translate Script
Automates translation using Google Translate web interface with Microsoft Edge.

Usage:
    python auto_translate_google.py <input_file> --target-lang <language> [options]

Example:
    python auto_translate_google.py video.txt --target-lang English
    python auto_translate_google.py video_sanitized.txt --target-lang en --source-lang vi
"""

import os
import sys
import time
import argparse
import pyperclip
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.microsoft import EdgeChromiumDriverManager


# Language code mapping for Google Translate
LANGUAGE_CODES = {
    'english': 'en',
    'vietnamese': 'vi',
    'spanish': 'es',
    'french': 'fr',
    'german': 'de',
    'chinese': 'zh-CN',
    'japanese': 'ja',
    'korean': 'ko',
    'thai': 'th',
    'russian': 'ru',
    'portuguese': 'pt',
    'italian': 'it',
    'arabic': 'ar',
    'hindi': 'hi',
}


def get_language_code(language):
    """
    Convert language name to Google Translate language code.
    
    Args:
        language: Language name or code
        
    Returns:
        str: Language code for Google Translate
    """
    if not language:
        return 'auto'
    
    # If already a code, return as-is
    if len(language) == 2 or (len(language) == 5 and '-' in language):
        return language.lower()
    
    # Convert name to code
    lang_lower = language.lower()
    return LANGUAGE_CODES.get(lang_lower, lang_lower)


def setup_edge_driver(headless=False):
    """
    Set up Microsoft Edge WebDriver.
    
    Args:
        headless: Whether to run browser in headless mode
        
    Returns:
        WebDriver instance
    """
    print("Setting up Microsoft Edge driver...")
    
    edge_options = Options()
    if headless:
        edge_options.add_argument('--headless')
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_options.add_argument('--window-size=1920,1080')
    edge_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Suppress logging
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    edge_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Try to use webdriver-manager first
        try:
            service = Service(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)
        except:
            # Fall back to system Edge driver
            print("Trying system Edge driver...")
            driver = webdriver.Edge(options=edge_options)
        
        return driver
    except Exception as e:
        print(f"Error setting up Edge driver: {e}")
        print("\nPlease ensure Microsoft Edge is installed.")
        print("You may need to download msedgedriver.exe manually:")
        print("https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        sys.exit(1)


def translate_with_google(text, source_lang='auto', target_lang='en', headless=False, wait_time=10):
    """
    Translate text using Google Translate web interface.
    
    Args:
        text: Text to translate
        source_lang: Source language code (default: auto-detect)
        target_lang: Target language code
        headless: Run browser in headless mode
        wait_time: Maximum wait time for elements (seconds)
        
    Returns:
        str: Translated text
    """
    driver = None
    try:
        # Setup driver
        driver = setup_edge_driver(headless=headless)
        
        # Build Google Translate URL
        url = f"https://translate.google.com/?sl={source_lang}&tl={target_lang}&op=translate"
        print(f"\nOpening Google Translate ({source_lang} → {target_lang})...")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, wait_time)
        
        # Find and fill source text area
        print("Entering text to translate...")
        try:
            # Try multiple possible selectors for the input textarea
            source_textarea = None
            selectors = [
                "textarea[aria-label*='Source text']",
                "textarea[aria-label*='Văn bản nguồn']",
                "textarea.er8xn",
                "textarea[jsname]",
            ]
            
            for selector in selectors:
                try:
                    source_textarea = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not source_textarea:
                raise Exception("Could not find source text input")
            
            # Clear and enter text
            source_textarea.clear()
            source_textarea.send_keys(text)
            
            # Wait for translation to appear
            print("Waiting for translation...")
            time.sleep(3)  # Give it time to translate
            
            # Find the copy button on the target side
            print("Looking for copy button...")
            copy_button = None
            copy_selectors = [
                "button[aria-label*='Copy translation']",
                "button[aria-label*='Sao chép bản dịch']",
                "button.VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.YJBIwf",
                "button[jsname='W297wb']",
            ]
            
            for selector in copy_selectors:
                try:
                    copy_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not copy_button:
                # Try to get translation text directly
                print("Copy button not found, trying to get text directly...")
                translation_selectors = [
                    "span[jsname='W297wb']",
                    "span.ryNqvb",
                    "div.J0lOec span",
                ]
                
                for selector in translation_selectors:
                    try:
                        translation_element = driver.find_element(By.CSS_SELECTOR, selector)
                        translated_text = translation_element.text
                        if translated_text and translated_text != text:
                            print("✓ Translation retrieved directly")
                            return translated_text
                    except:
                        continue
                
                raise Exception("Could not find translation or copy button")
            
            # Click copy button
            print("Clicking copy button...")
            copy_button.click()
            time.sleep(1)
            
            # Get text from clipboard
            print("Getting text from clipboard...")
            translated_text = pyperclip.paste()
            
            if not translated_text or translated_text == text:
                raise Exception("Translation appears to be empty or same as input")
            
            print("✓ Translation copied successfully")
            return translated_text
            
        except TimeoutException:
            print("Timeout waiting for page elements")
            raise
        except Exception as e:
            print(f"Error during translation: {e}")
            # Take screenshot for debugging
            screenshot_path = "error_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            raise
            
    finally:
        if driver:
            driver.quit()


def process_file(input_file, target_lang='en', source_lang='auto', output_file=None, headless=False):
    """
    Process a file through Google Translate automation.
    
    Args:
        input_file: Path to input text file
        target_lang: Target language for translation
        source_lang: Source language (auto-detect if not specified)
        output_file: Path to output file (optional)
        headless: Run browser in headless mode
    """
    print("=" * 60)
    print("GOOGLE TRANSLATE AUTOMATION")
    print("=" * 60)
    
    # Read input file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    print(f"\nReading: {input_file}")
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    
    if not text:
        print("Error: Input file is empty")
        sys.exit(1)
    
    print(f"Text length: {len(text)} characters")
    
    # Warn if text is very long
    if len(text) > 5000:
        print("\n⚠ Warning: Text is quite long. Google Translate may have character limits.")
        print("Consider splitting into smaller chunks if translation fails.")
    
    # Convert language names to codes
    source_code = get_language_code(source_lang)
    target_code = get_language_code(target_lang)
    
    # Perform translation
    try:
        translated_text = translate_with_google(
            text, 
            source_lang=source_code,
            target_lang=target_code,
            headless=headless
        )
    except Exception as e:
        print(f"\n❌ Translation failed: {e}")
        sys.exit(1)
    
    # Determine output file path
    if not output_file:
        # Create output filename with _autotranslated.txt suffix
        base_name = input_path.stem
        output_file = input_path.parent / f"{base_name}_autotranslated.txt"
    else:
        output_file = Path(output_file)
    
    # Save translated text
    print(f"\nSaving translation to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_text)
    
    print("\n" + "=" * 60)
    print("TRANSLATION COMPLETE")
    print("=" * 60)
    print(f"\n✓ Output file: {output_file}")
    print(f"✓ Translation length: {len(translated_text)} characters")


def main():
    parser = argparse.ArgumentParser(
        description='Automate Google Translate using Microsoft Edge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate Vietnamese to English (auto-detect source)
  python auto_translate_google.py input.txt --target-lang English
  
  # Specify both source and target languages
  python auto_translate_google.py input.txt --source-lang vi --target-lang en
  
  # Save to custom output file
  python auto_translate_google.py input.txt --target-lang English --output translated.txt
  
  # Run in headless mode (no browser window)
  python auto_translate_google.py input.txt --target-lang English --headless

Supported languages:
  English, Vietnamese, Spanish, French, German, Chinese, Japanese, 
  Korean, Thai, Russian, Portuguese, Italian, Arabic, Hindi
  
  You can also use language codes: en, vi, es, fr, de, zh-CN, ja, ko, etc.
        """
    )
    
    parser.add_argument('input_file', help='Input text file to translate')
    parser.add_argument('--target-lang', '-t', required=True, 
                       help='Target language (e.g., English, en)')
    parser.add_argument('--source-lang', '-s', default='auto',
                       help='Source language (default: auto-detect)')
    parser.add_argument('--output', '-o',
                       help='Output file path (default: input_file_autotranslated.txt)')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode (no visible window)')
    
    args = parser.parse_args()
    
    process_file(
        input_file=args.input_file,
        target_lang=args.target_lang,
        source_lang=args.source_lang,
        output_file=args.output,
        headless=args.headless
    )


if __name__ == '__main__':
    main()
