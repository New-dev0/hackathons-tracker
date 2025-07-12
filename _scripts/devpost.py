import requests
import json
from datetime import datetime

def fetch_hackathons(max_pages=5):
    """Fetch hackathons from multiple pages"""
    all_hackathons = []
    base_url = "https://devpost.com/api/hackathons"
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        response = requests.get(url)
        data = response.json()
        
        if not data.get("hackathons"):
            break
            
        all_hackathons.extend(data["hackathons"])
        
        # Check if we've reached the last page
        if len(data["hackathons"]) < 9:  # Default page size is 9
            break
    
    return {"hackathons": all_hackathons}

def format_themes(themes):
    return ", ".join([theme["name"] for theme in themes])

def clean_prize_amount(prize_amount):
    # Remove HTML tags and clean up the prize amount
    return prize_amount.replace('\u003cspan data-currency-value\u003e', '').replace('\u003c/span\u003e', '')

def get_location_with_icon(displayed_location):
    """Convert location icon name to emoji and combine with location"""
    icon_map = {
        'globe': '🌐',
        'map-marker-alt': '📍',
        'building': '🏢',
        'university': '🎓',
        'home': '🏠',
    }
    icon = icon_map.get(displayed_location['icon'], '📌')  # Default icon if not found
    return f"{icon} {displayed_location['location']}"

def get_status_emoji(open_state):
    """Get emoji based on hackathon status"""
    status_map = {
        'open': '🟢',      # Green circle for open hackathons
        'upcoming': '⏳',   # Hourglass for upcoming hackathons
        'closed': '🔴',    # Red circle for closed hackathons
    }
    return status_map.get(open_state, '❔')  # Question mark for unknown status

def create_markdown_table(hackathons):
    table = [
        "| Status | Title | Location | Submission Period | Prize | Themes |",
        "|--------|--------|----------|-------------------|-------|--------|"
    ]
    
    for hackathon in hackathons["hackathons"]:
        status = get_status_emoji(hackathon['open_state'])
        title = f"[{hackathon['title']}]({hackathon['url']})"
        location = get_location_with_icon(hackathon['displayed_location'])
        
        # Use submission period dates instead of time left for consistency
        submission_period = hackathon['submission_period_dates']
        
        prize = clean_prize_amount(hackathon['prize_amount'])
        themes = format_themes(hackathon['themes'])
        
        row = f"| {status} | {title} | {location} | {submission_period} | {prize} | {themes} |"
        table.append(row)
    
    return "\n".join(table)

def update_readme(table_content):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the DevPost section and update it
    sections = content.split("### DevPost")
    if len(sections) < 2:
        return False
    
    # Add the table after the DevPost heading
    new_content = sections[0] + "### DevPost\n\n" + table_content + "\n"
    
    # Add any remaining sections
    if len(sections) > 2:
        new_content += "\n" + "### DevPost".join(sections[2:])
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    return True

def main():
    # Fetch 5 pages of hackathons by default
    hackathons = fetch_hackathons(max_pages=5)
    print(f"Found {len(hackathons['hackathons'])} hackathons")
    
    table = create_markdown_table(hackathons)
    success = update_readme(table)
    if success:
        print("README.md has been updated successfully!")
    else:
        print("Failed to update README.md")

if __name__ == "__main__":
    main() 