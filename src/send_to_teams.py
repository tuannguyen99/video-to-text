#!/usr/bin/env python3
"""
Send to Microsoft Teams Module
Sends translated files to a Microsoft Teams channel via webhook.

Usage:
    python send_to_teams.py <file_path> --webhook <webhook_url> [options]

Example:
    python send_to_teams.py output.txt --webhook "https://outlook.office.com/webhook/..."
    python send_to_teams.py output.txt --webhook "https://..." --title "Translation Complete"
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime


def read_webhook_from_config(config_file="teams_config.json"):
    """
    Read Teams webhook URL from configuration file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        str: Webhook URL or None
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('webhook_url')
    except Exception as e:
        print(f"Warning: Could not read config file: {e}")
    return None


def save_webhook_to_config(webhook_url, config_file="teams_config.json"):
    """
    Save Teams webhook URL to configuration file.
    
    Args:
        webhook_url: Webhook URL to save
        config_file: Path to configuration file
    """
    try:
        config = {'webhook_url': webhook_url}
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Webhook URL saved to {config_file}")
    except Exception as e:
        print(f"Warning: Could not save webhook URL: {e}")


def create_teams_message(file_path, title=None, include_content=True, max_content_length=1000):
    """
    Create a formatted message for Microsoft Teams.
    
    Args:
        file_path: Path to the file
        title: Custom title for the message
        include_content: Whether to include file content in message
        max_content_length: Maximum length of content to include
        
    Returns:
        dict: Teams message payload
    """
    file_path = Path(file_path)
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f"[Error reading file: {e}]"
    
    # Get file stats
    file_size = file_path.stat().st_size
    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
    
    # Determine title
    if not title:
        if "_autotranslated" in file_path.name:
            title = "🌐 Auto Translation Complete"
        elif "_translation_" in file_path.name:
            title = "🌐 Translation Complete (Ollama)"
        elif "_summary_" in file_path.name:
            title = "📝 Summary Complete"
        else:
            title = "📄 File Ready"
    
    # Truncate content if too long
    content_preview = content
    if len(content) > max_content_length:
        content_preview = content[:max_content_length] + f"\n\n... (truncated, total {len(content)} characters)"
    
    # Create adaptive card message
    message = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": title,
        "themeColor": "0078D4",
        "title": title,
        "sections": [
            {
                "activityTitle": f"**{file_path.name}**",
                "activitySubtitle": f"Created: {file_modified.strftime('%Y-%m-%d %H:%M:%S')}",
                "facts": [
                    {
                        "name": "File Name:",
                        "value": file_path.name
                    },
                    {
                        "name": "File Size:",
                        "value": f"{file_size:,} bytes ({file_size / 1024:.2f} KB)"
                    },
                    {
                        "name": "Location:",
                        "value": str(file_path.parent)
                    },
                    {
                        "name": "Characters:",
                        "value": f"{len(content):,}"
                    }
                ],
                "markdown": True
            }
        ]
    }
    
    # Add content preview if requested
    if include_content and content_preview:
        message["sections"].append({
            "activityTitle": "📄 Content Preview:",
            "text": f"```\n{content_preview}\n```",
            "markdown": True
        })
    
    # Add potential actions
    message["potentialAction"] = [
        {
            "@type": "OpenUri",
            "name": "📂 Open Folder",
            "targets": [
                {
                    "os": "default",
                    "uri": f"file:///{file_path.parent.as_posix()}"
                }
            ]
        }
    ]
    
    return message


def send_to_teams(webhook_url, message):
    """
    Send message to Microsoft Teams via webhook.
    
    Args:
        webhook_url: Teams webhook URL
        message: Message payload (dict)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            webhook_url,
            headers=headers,
            data=json.dumps(message),
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error: Teams API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Teams: {e}")
        return False


def send_file_to_teams(file_path, webhook_url=None, title=None, include_content=True, 
                       max_content_length=1000, save_webhook=False):
    """
    Send a file notification to Microsoft Teams.
    
    Args:
        file_path: Path to the file to send
        webhook_url: Teams webhook URL (optional if saved in config)
        title: Custom title for the message
        include_content: Whether to include file content
        max_content_length: Maximum content length to include
        save_webhook: Whether to save webhook URL to config
        
    Returns:
        bool: True if successful, False otherwise
    """
    print("=" * 60)
    print("SEND TO MICROSOFT TEAMS")
    print("=" * 60)
    
    # Validate file
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return False
    
    print(f"\nFile: {file_path.name}")
    print(f"Size: {file_path.stat().st_size:,} bytes")
    
    # Get webhook URL
    if not webhook_url:
        webhook_url = read_webhook_from_config()
        if not webhook_url:
            print("\nError: No webhook URL provided.")
            print("Please provide webhook URL via --webhook option or save it in teams_config.json")
            print("\nTo get a webhook URL:")
            print("1. Open Microsoft Teams")
            print("2. Go to your channel")
            print("3. Click '...' → Connectors → Incoming Webhook")
            print("4. Configure and copy the webhook URL")
            return False
    
    # Save webhook if requested
    if save_webhook:
        save_webhook_to_config(webhook_url)
    
    # Create message
    print("\nCreating Teams message...")
    message = create_teams_message(
        file_path, 
        title=title, 
        include_content=include_content,
        max_content_length=max_content_length
    )
    
    # Send to Teams
    print("Sending to Teams channel...")
    success = send_to_teams(webhook_url, message)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ MESSAGE SENT SUCCESSFULLY!")
        print("=" * 60)
        print("\nCheck your Teams channel for the notification.")
        return True
    else:
        print("\n" + "=" * 60)
        print("✗ FAILED TO SEND MESSAGE")
        print("=" * 60)
        print("\nPlease check:")
        print("1. Webhook URL is correct")
        print("2. Webhook is not expired")
        print("3. You have internet connection")
        return False


def send_multiple_files(file_paths, webhook_url=None, title=None, include_content=True):
    """
    Send multiple files to Teams in a single message.
    
    Args:
        file_paths: List of file paths
        webhook_url: Teams webhook URL
        title: Custom title
        include_content: Whether to include content
        
    Returns:
        bool: True if successful
    """
    if not webhook_url:
        webhook_url = read_webhook_from_config()
        if not webhook_url:
            print("Error: No webhook URL configured")
            return False
    
    # Create message with multiple files
    message = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": title or "📦 Multiple Files Ready",
        "themeColor": "0078D4",
        "title": title or "📦 Multiple Files Ready",
        "sections": []
    }
    
    for file_path in file_paths:
        file_path = Path(file_path)
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            content = "[Error reading file]"
        
        section = {
            "activityTitle": f"**{file_path.name}**",
            "facts": [
                {"name": "Size:", "value": f"{file_path.stat().st_size:,} bytes"},
                {"name": "Characters:", "value": f"{len(content):,}"}
            ]
        }
        
        if include_content:
            preview = content[:500] + ("..." if len(content) > 500 else "")
            section["text"] = f"```\n{preview}\n```"
        
        message["sections"].append(section)
    
    return send_to_teams(webhook_url, message)


def main():
    parser = argparse.ArgumentParser(
        description='Send file notifications to Microsoft Teams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send with webhook URL:
  python send_to_teams.py output.txt --webhook "https://outlook.office.com/webhook/..."
  
  # Save webhook for future use:
  python send_to_teams.py output.txt --webhook "https://..." --save-webhook
  
  # Use saved webhook:
  python send_to_teams.py output.txt
  
  # Custom title:
  python send_to_teams.py output.txt --title "Translation Complete!"
  
  # Don't include content preview:
  python send_to_teams.py output.txt --no-content
  
  # Send multiple files:
  python send_to_teams.py file1.txt file2.txt file3.txt

How to get a Teams webhook URL:
  1. Open Microsoft Teams
  2. Navigate to your channel
  3. Click '...' (More options) next to the channel name
  4. Select 'Connectors' or 'Workflows'
  5. Search for 'Incoming Webhook'
  6. Click 'Configure' or 'Add'
  7. Give it a name (e.g., "Translation Bot")
  8. Copy the webhook URL
  9. Click 'Done'
        """
    )
    
    parser.add_argument('file_paths', nargs='+', help='File(s) to send notification about')
    parser.add_argument('--webhook', '-w', help='Microsoft Teams webhook URL')
    parser.add_argument('--title', '-t', help='Custom title for the message')
    parser.add_argument('--no-content', action='store_true', 
                       help='Do not include file content in message')
    parser.add_argument('--max-length', type=int, default=1000,
                       help='Maximum content length to include (default: 1000)')
    parser.add_argument('--save-webhook', action='store_true',
                       help='Save webhook URL to config file for future use')
    parser.add_argument('--config', default='teams_config.json',
                       help='Configuration file path (default: teams_config.json)')
    
    args = parser.parse_args()
    
    # Handle multiple files
    if len(args.file_paths) > 1:
        success = send_multiple_files(
            args.file_paths,
            webhook_url=args.webhook,
            title=args.title,
            include_content=not args.no_content
        )
    else:
        success = send_file_to_teams(
            file_path=args.file_paths[0],
            webhook_url=args.webhook,
            title=args.title,
            include_content=not args.no_content,
            max_content_length=args.max_length,
            save_webhook=args.save_webhook
        )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
