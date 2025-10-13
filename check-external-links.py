import os
import re
import requests
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

def extract_external_links(content_dir):
    """Extract all external HTTP(S) links from markdown files"""
    external_links = defaultdict(list)
    
    for root, dirs, files in os.walk(content_dir):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                # Make path relative for cleaner output
                rel_path = filepath.replace(content_dir + '/', '')
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Find markdown links [text](url)
                    md_links = re.findall(r'\[([^\]]*)\]\((https?://[^\)]+)\)', content)
                    
                    # Find HTML links
                    html_links = re.findall(r'href=["\']((https?://[^"\']+))["\']', content)
                    
                    for text, url in md_links:
                        # Clean up URL
                        url = url.split()[0] if ' ' in url else url
                        external_links[rel_path].append(('markdown', text, url))
                    
                    for url_match in html_links:
                        url = url_match[0] if isinstance(url_match, tuple) else url_match
                        url = url.split()[0] if ' ' in url else url
                        external_links[rel_path].append(('html', '', url))
                
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return external_links

def check_url(url, timeout=10):
    """Check if a URL is accessible"""
    try:
        # Try HEAD first (faster)
        response = requests.head(url, timeout=timeout, allow_redirects=True,
                                headers={'User-Agent': 'Mozilla/5.0 (compatible; LinkChecker/1.0)'})
        
        # Some servers don't support HEAD, try GET if HEAD fails
        if response.status_code >= 400:
            response = requests.get(url, timeout=timeout, allow_redirects=True,
                                   headers={'User-Agent': 'Mozilla/5.0 (compatible; LinkChecker/1.0)'})
        
        return url, response.status_code, None
    except requests.exceptions.Timeout:
        return url, None, "Timeout"
    except requests.exceptions.ConnectionError:
        return url, None, "Connection error"
    except requests.exceptions.TooManyRedirects:
        return url, None, "Too many redirects"
    except requests.exceptions.RequestException as e:
        return url, None, str(e)[:100]

def check_links_parallel(links, max_workers=10):
    """Check multiple URLs in parallel"""
    unique_urls = set()
    for file_links in links.values():
        for link_type, text, url in file_links:
            unique_urls.add(url)
    
    print(f"\nChecking {len(unique_urls)} unique URLs...")
    print("This may take 10-30 minutes depending on the number of links.\n")
    
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in unique_urls}
        
        completed = 0
        for future in as_completed(future_to_url):
            url, status, error = future.result()
            results[url] = (status, error)
            
            completed += 1
            if completed % 10 == 0:
                print(f"Progress: {completed}/{len(unique_urls)} URLs checked ({(completed/len(unique_urls)*100):.1f}%)")
            
            time.sleep(0.1)  # Be nice to servers
    
    return results

if __name__ == "__main__":
    print("=" * 70)
    print("EXTERNAL LINKS CHECKER")
    print("=" * 70)
    
    print("\nExtracting external links from content...")
    external_links = extract_external_links('content/')
    
    total_links = sum(len(links) for links in external_links.values())
    print(f"Found {total_links} external links across {len(external_links)} files")
    
    url_status = check_links_parallel(external_links, max_workers=10)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    
    # Categorize results
    broken_links = []
    working_links = []
    timeout_links = []
    
    for filepath, links in external_links.items():
        for link_type, text, url in links:
            status, error = url_status.get(url, (None, "Not checked"))
            
            if status is None:
                if error == "Timeout":
                    timeout_links.append({
                        'file': filepath,
                        'type': link_type,
                        'text': text,
                        'url': url,
                        'status': None,
                        'error': error
                    })
                else:
                    broken_links.append({
                        'file': filepath,
                        'type': link_type,
                        'text': text,
                        'url': url,
                        'status': None,
                        'error': error
                    })
            elif status >= 400:
                broken_links.append({
                    'file': filepath,
                    'type': link_type,
                    'text': text,
                    'url': url,
                    'status': status,
                    'error': error
                })
            else:
                working_links.append({
                    'file': filepath,
                    'type': link_type,
                    'text': text,
                    'url': url,
                    'status': status
                })
    
    # Generate markdown report
    with open('AUDIT-06-external-links.md', 'w') as f:
        f.write('# External Links Audit Report\n')
        f.write('## joshuapsteele.com Hugo Site\n\n')
        f.write('**Audit Date:** October 11, 2025\n')
        f.write(f'**Total Files Analyzed:** {len(external_links)}\n\n')
        f.write('---\n\n')
        
        f.write('## 📊 Summary Statistics\n\n')
        f.write(f'- **Total external links:** {total_links}\n')
        f.write(f'- **Unique URLs checked:** {len(url_status)}\n')
        f.write(f'- **Working links:** {len(working_links)} ({len(working_links)/total_links*100:.1f}%)\n')
        f.write(f'- **Broken/error links:** {len(broken_links)} ({len(broken_links)/total_links*100:.1f}%)\n')
        f.write(f'- **Timeout links:** {len(timeout_links)} ({len(timeout_links)/total_links*100:.1f}%)\n\n')
        
        if broken_links:
            f.write('---\n\n')
            f.write('## ❌ Broken External Links\n\n')
            f.write(f'**Total broken/inaccessible links:** {len(broken_links)}\n\n')
            
            # Group by file
            by_file = defaultdict(list)
            for item in broken_links:
                by_file[item['file']].append(item)
            
            f.write(f'**Files affected:** {len(by_file)}\n\n')
            
            for filepath in sorted(by_file.keys()):
                items = by_file[filepath]
                f.write(f'\n### {filepath}\n\n')
                f.write(f'**Broken links:** {len(items)}\n\n')
                for item in items:
                    status_str = f"Status {item['status']}" if item['status'] else "ERROR"
                    f.write(f"- **{status_str}**: ")
                    if item['text']:
                        f.write(f"`[{item['text']}]({item['url']})`")
                    else:
                        f.write(f"`{item['url']}`")
                    if item['error']:
                        f.write(f"\n  - Error: {item['error']}")
                    f.write('\n')
        else:
            f.write('---\n\n')
            f.write('## ✅ All External Links Working!\n\n')
            f.write('No broken external links found.\n\n')
        
        if timeout_links:
            f.write('\n---\n\n')
            f.write('## ⏱️  Timeout Links\n\n')
            f.write(f'**Links that timed out:** {len(timeout_links)}\n\n')
            f.write('These URLs took too long to respond. They may be working but slow, or temporarily unavailable.\n\n')
            
            # Show unique timeout URLs
            timeout_urls = set(item['url'] for item in timeout_links)
            for url in sorted(timeout_urls):
                f.write(f'- `{url}`\n')
        
        f.write('\n---\n\n')
        f.write('## 💡 Recommendations\n\n')
        
        if broken_links or timeout_links:
            f.write('### Immediate Actions\n\n')
            f.write('1. **Review broken links** - Some may have moved to new URLs\n')
            f.write('2. **Use Internet Archive** - For historical references that are no longer available\n')
            f.write('3. **Update or remove** - Fix URLs or remove dead links\n')
            f.write('4. **Re-check timeout links** - They may work on retry\n\n')
            
            f.write('### Common Issues\n\n')
            f.write('- **404 errors** - Page moved or deleted\n')
            f.write('- **Connection errors** - Domain no longer exists\n')
            f.write('- **Timeouts** - Server too slow or overloaded\n')
            f.write('- **SSL errors** - Certificate issues\n\n')
        
        f.write('### Prevention\n\n')
        f.write('1. Use archived versions for historical references\n')
        f.write('2. Link to stable, authoritative sources when possible\n')
        f.write('3. Run this check quarterly\n')
        f.write('4. Consider using a link checker service\n\n')
        
        f.write('---\n\n')
        f.write('*Generated by Phase 2, Task 2.2 of Content Audit*\n')
    
    # Save JSON data
    json_data = {
        'total_files': len(external_links),
        'total_links': total_links,
        'unique_urls': len(url_status),
        'working_links': len(working_links),
        'broken_links': len(broken_links),
        'timeout_links': len(timeout_links),
        'broken_details': broken_links,
        'timeout_details': timeout_links
    }
    
    with open('audit-external-links.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\n✅ Report saved: AUDIT-06-external-links.md")
    print(f"✅ Data saved: audit-external-links.json")
    print(f"\nResults:")
    print(f"  Working links: {len(working_links)}")
    print(f"  Broken links: {len(broken_links)}")
    print(f"  Timeout links: {len(timeout_links)}")
    
    if broken_links:
        print(f"\nTop 10 files with broken links:")
        file_counts = defaultdict(int)
        for item in broken_links:
            file_counts[item['file']] += 1
        for filepath, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {filepath} ({count} broken links)")

