import requests
import json
import re
import time

BASE_URL = "https://nanobananaprompt.club"
# Multiple tags to scrape
TAGS = ["marketing", "product", "photography", "cinematic"]

def find_supabase_config():
    """Find Supabase configuration from the page"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    })
    
    response = session.get(f"{BASE_URL}/prompts?tags={TAGS[0]}")
    html = response.text
    
    # Look for Supabase URL pattern
    supabase_url_pattern = r'https://[a-zA-Z0-9]+\.supabase\.co'
    supabase_urls = re.findall(supabase_url_pattern, html)
    
    # Look for anon key pattern (JWT format)
    key_pattern = r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'
    keys = re.findall(key_pattern, html)
    
    print("Found Supabase URLs:", supabase_urls)
    print("Found potential keys:", len(keys))
    
    if supabase_urls and keys:
        return supabase_urls[0], keys[0]
    
    return None, None

def scrape_supabase_api(supabase_url, api_key, tag, page=0, page_size=50):
    """Scrape using Supabase REST API"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    
    all_results = []
    offset = page * page_size
    
    while True:
        # Query prompts table with tag filter
        url = f"{supabase_url}/rest/v1/prompts"
        params = {
            "select": "*",
            "tags": f"cs.{{\"{tag}\"}}",  # contains tag
            "order": "created_at.desc",
            "offset": offset,
            "limit": page_size
        }
        
        try:
            response = session.get(url, params=params)
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code}")
                print(response.text[:500])
                break
            
            data = response.json()
            
            if not data:
                print("No more data")
                break
            
            for item in data:
                all_results.append({
                    'id': item.get('id'),
                    'image_url': item.get('image_url') or item.get('thumbnail_url') or item.get('media_url'),
                    'prompt': item.get('prompt') or item.get('text') or item.get('description'),
                    'tags': item.get('tags', []),
                    'source_tag': tag,
                })
            
            print(f"Fetched {len(data)} items, total: {len(all_results)}")
            
            if len(data) < page_size:
                break
            
            offset += page_size
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    return all_results

def scrape_alternative_api(tag):
    """Scrape the discovered API with pagination for a specific tag"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    
    all_results = []
    page = 1
    page_size = 50
    
    while True:
        endpoint = f"{BASE_URL}/api/prompts?tags={tag}&page={page}&limit={page_size}"
        
        try:
            print(f"  Fetching page {page}...")
            response = session.get(endpoint)
            
            if response.status_code != 200:
                print(f"  Error: {response.status_code}")
                break
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                print(f"  No more items for tag: {tag}")
                break
            
            for item in items:
                # Extract image URL (camelCase field)
                image_url = item.get('imageUrl') or item.get('sourceUrl')
                
                # Fallback to imageUrls array
                if not image_url and item.get('imageUrls'):
                    image_url = item['imageUrls'][0]
                
                all_results.append({
                    'id': item.get('id'),
                    'image_url': image_url,
                    'image_urls': item.get('imageUrls', []) or ([item.get('imageUrl')] if item.get('imageUrl') else []),
                    'prompt': item.get('prompt', ''),
                    'tags': item.get('tags', []),
                    'title': item.get('title', ''),
                    'model': item.get('model', ''),
                    'source_tag': tag,
                })
            
            print(f"    Fetched {len(items)} items, total for {tag}: {len(all_results)}")
            
            # Check if there's more
            has_more = data.get('hasMore', False)
            if not has_more:
                print(f"  No more pages for tag: {tag}")
                break
            
            page += 1
            time.sleep(0.3)  # Be nice to the server
            
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    return all_results

def main():
    print("Scraping Nano Banana Prompts...")
    print("=" * 50)
    
    all_results = []
    seen_ids = set()  # Track seen IDs to avoid duplicates
    
    # First, find Supabase config
    print("\n[1] Looking for Supabase configuration...")
    supabase_url, api_key = find_supabase_config()
    
    # Scrape each tag
    for tag in TAGS:
        print(f"\n[Scraping tag: {tag}]")
        if supabase_url and api_key:
            print(f"[2] Found Supabase config. Scraping API...")
            results = scrape_supabase_api(supabase_url, api_key, tag)
        else:
            results = scrape_alternative_api(tag)
        
        # Add results, avoiding duplicates
        for item in results:
            if item['id'] not in seen_ids:
                seen_ids.add(item['id'])
                all_results.append(item)
        
        print(f"  Total unique prompts so far: {len(all_results)}")
    
    print(f"\n{'=' * 50}")
    print(f"Total unique prompts found: {len(all_results)}")
    
    # Count by source tag
    tag_counts = {}
    for item in all_results:
        source = item.get('source_tag', 'unknown')
        tag_counts[source] = tag_counts.get(source, 0) + 1
    print("Breakdown by source tag:")
    for tag, count in tag_counts.items():
        print(f"  {tag}: {count}")
    
    # Print sample
    for i, item in enumerate(all_results[:5] if all_results else [], 1):
        print(f"\n[{i}]")
        print(f"Image: {item.get('image_url', 'N/A')}")
        prompt = str(item.get('prompt', 'N/A'))
        print(f"Prompt: {prompt[:150]}..." if len(prompt) > 150 else f"Prompt: {prompt}")
        print(f"Tags: {item.get('tags', [])}")
    
    # Save results
    output_file = "all_prompts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(all_results)} prompts to {output_file}")
    
    return all_results

if __name__ == "__main__":
    main()