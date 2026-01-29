#!/usr/bin/env python3
"""
Test script to verify that the API returns description and location for pending events
"""

import requests
import json

# Configuration
API_URL = "http://localhost:5800"  # Default API URL
API_KEY = "your-secret-api-key-here"  # Default API key from config

def test_pending_events_api():
    """Test the pending events API endpoint"""
    print("Testing pending events API endpoint...")
    
    # Make request to the API
    headers = {
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.get(f"{API_URL}/events/pending", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            
            # Check if events contain description and location
            if 'events' in data:
                events = data['events']
                print(f"\nFound {len(events)} events")
                
                for i, event in enumerate(events):
                    print(f"\nEvent {i+1}:")
                    print(f"  Title: {event.get('title', 'N/A')}")
                    print(f"  Description: {event.get('description', 'N/A')}")
                    print(f"  Location: {event.get('location', 'N/A')}")
            else:
                print("No events found in response")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_pending_events_api()