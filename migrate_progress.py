#!/usr/bin/env python3
"""
Migrate outside hours from one Dreaming account to another account.
"""

import requests
import json
import sys
from typing import List, Dict, Any


def get_external_time(token: str, language: str = "es") -> List[Dict[str, Any]]:
    """
    Fetch all external time entries for a given language.
    
    Args:
        token: Bearer token for authentication
        language: Language code ('es' for Spanish, 'fr' for French)
    
    Returns:
        List of time entries
    """
    url = f"https://app.dreaming.com/.netlify/functions/externalTime?language={language}"
    headers = {
        "accept": "*/*",
        "authorization": f"Bearer {token}",
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def post_external_time(token: str, entry: Dict[str, Any], language: str = "fr") -> Dict[str, Any]:
    """
    Post a time entry to the specified language.
    
    Args:
        token: Bearer token for authentication
        entry: Time entry data to post
        language: Target language code ('fr' for French)
    
    Returns:
        Response data
    """
    url = f"https://app.dreaming.com/.netlify/functions/externalTime?language={language}"
    headers = {
        "accept": "*/*",
        "authorization": f"Bearer {token}",
        "content-type": "text/plain;charset=UTF-8",
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(entry))
    response.raise_for_status()
    
    return response.json()


def migrate_progress(source_token: str, target_token: str, source_lang: str = "es", target_lang: str = "fr", dry_run: bool = True):
    """
    Migrate progress from source account/language to target account/language.
    
    Args:
        source_token: Bearer token for the source account
        target_token: Bearer token for the target account
        source_lang: Source language code ('es' or 'fr')
        target_lang: Target language code ('es' or 'fr')
        dry_run: If True, only show what would be migrated without actually posting
    """
    lang_names = {'es': 'Spanish', 'fr': 'French'}
    print(f"Fetching {lang_names.get(source_lang, source_lang)} progress from source account...")
    try:
        response_data = get_external_time(source_token, language=source_lang)
        print(f"DEBUG: Response type: {type(response_data)}")
        print(f"DEBUG: Raw response: {response_data[:500] if isinstance(response_data, str) else response_data}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

    # Normalize response into a list of entries
    entries = []
    if isinstance(response_data, list):
        entries = response_data
    elif isinstance(response_data, dict):
        # Try common keys including externalTimes (used by Dreaming API)
        for key in ("externalTimes", "entries", "data", "items", "results"):
            if key in response_data and isinstance(response_data[key], list):
                entries = response_data[key]
                break
        else:
            entries = [response_data]
    elif isinstance(response_data, str):
        # Sometimes APIs double-encode JSON; try to parse
        try:
            parsed = json.loads(response_data)
            if isinstance(parsed, list):
                entries = parsed
            elif isinstance(parsed, dict):
                entries = parsed.get("externalTimes") or parsed.get("entries") or parsed.get("data") or [parsed]
            else:
                entries = [response_data]
        except Exception:
            entries = [response_data]

    # Convert any string entries to dicts when possible
    normalized_entries = []
    for e in entries:
        if isinstance(e, dict):
            normalized_entries.append(e)
        elif isinstance(e, str):
            try:
                maybe = json.loads(e)
                if isinstance(maybe, dict):
                    normalized_entries.append(maybe)
                else:
                    # Skip non-dict entries we can't interpret
                    pass
            except Exception:
                # Skip strings that aren't JSON objects
                pass
        # Ignore other unexpected types

    entries = normalized_entries

    print(f"Found {len(entries)} time entries")
    
    if not entries:
        print("No entries to migrate")
        return
    
    # Display summary
    total_seconds = sum(entry.get('timeSeconds', 0) for entry in entries)
    total_hours = total_seconds / 3600
    print(f"Total time: {total_hours:.2f} hours ({total_seconds} seconds)")
    print()
    
    if dry_run:
        print("DRY RUN - showing first 5 entries that would be migrated:")
        for i, entry in enumerate(entries[:5]):
            print(f"\n{i+1}. {entry.get('description', 'No description')}")
            print(f"   Date: {entry.get('date', 'N/A')}")
            print(f"   Duration: {entry.get('timeSeconds', 0)} seconds")
            print(f"   Type: {entry.get('type', 'N/A')}")
            print(f"   URL: {entry.get('url', 'N/A')}")
        
        if len(entries) > 5:
            print(f"\n... and {len(entries) - 5} more entries")
        
        print("\nTo actually migrate, run with --execute flag")
        return
    
    # Actually migrate
    print(f"Migrating entries to {lang_names.get(target_lang, target_lang)} in target account...")
    success_count = 0
    error_count = 0
    
    for i, entry in enumerate(entries, 1):
        try:
            # Remove the 'id' field if present to let the target account create a new one
            entry_to_post = entry.copy()
            if 'id' in entry_to_post:
                del entry_to_post['id']
            
            # Add a new idempotency key to avoid conflicts
            import uuid
            entry_to_post['idempotencyKey'] = str(uuid.uuid4())
            
            post_external_time(target_token, entry_to_post, language=target_lang)
            success_count += 1
            
            if i % 10 == 0:
                print(f"Progress: {i}/{len(entries)} entries migrated")
        
        except requests.exceptions.RequestException as e:
            print(f"Error migrating entry {i}: {e}")
            error_count += 1
    
    print(f"\nMigration complete!")
    print(f"Successfully migrated: {success_count}")
    print(f"Errors: {error_count}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate progress from one Dreaming account/language to another"
    )
    parser.add_argument(
        "--source-token",
        required=True,
        help="Bearer token for the source account"
    )
    parser.add_argument(
        "--target-token",
        required=True,
        help="Bearer token for the target account"
    )
    parser.add_argument(
        "--source-language",
        default="es",
        choices=["es", "fr"],
        help="Source language code: es (Spanish) or fr (French). Default: es"
    )
    parser.add_argument(
        "--target-language",
        default="fr",
        choices=["es", "fr"],
        help="Target language code: es (Spanish) or fr (French). Default: fr"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the migration (default is dry-run)"
    )
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        print("Running in DRY RUN mode (no changes will be made)")
        print()
    
    migrate_progress(
        args.source_token, 
        args.target_token, 
        source_lang=args.source_language,
        target_lang=args.target_language,
        dry_run=dry_run
    )


if __name__ == "__main__":
    main()
