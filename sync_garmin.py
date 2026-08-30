import os
import json
from garminconnect import Garmin
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime, timedelta

# Load environment variables from .env file if it exists (for local testing)
if os.path.exists('.env'):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

def format_duration(seconds):
    """Convert seconds to minutes (rounded to 2 decimals)"""
    return round(seconds / 60, 2) if seconds else 0

def format_speed(distance_meters, duration_seconds):
    """Calculate speed in mph"""
    if not distance_meters or not duration_seconds:
        return 0
    distance_miles = distance_meters / 1609.34
    duration_hours = duration_seconds / 3600
    return round(distance_miles / duration_hours, 2)

def main():
    print("Starting Garmin cycling activities sync (Imperial Units)...")
    
    # Get credentials from environment variables
    garmin_email = os.environ.get('GARMIN_EMAIL')
    garmin_password = os.environ.get('GARMIN_PASSWORD')
    google_creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    sheet_id = os.environ.get('SHEET_ID')
    
    if not all([garmin_email, garmin_password, google_creds_json, sheet_id]):
        print("❌ Missing required environment variables")
        print(f"   GARMIN_EMAIL: {'✓' if garmin_email else '✗'}")
        print(f"   GARMIN_PASSWORD: {'✓' if garmin_password else '✗'}")
        print(f"   GOOGLE_CREDENTIALS: {'✓' if google_creds_json else '✗'}")
        print(f"   SHEET_ID: {'✓' if sheet_id else '✗'}")
        return
    
    # Connect to Garmin
    print("Connecting to Garmin...")
    try:
        garmin = Garmin(garmin_email, garmin_password)
        garmin.login()
        print("✅ Connected to Garmin")
    except Exception as e:
        print(f"❌ Failed to connect to Garmin: {e}")
        return
    
    # Get recent activities
    print("Fetching recent activities...")
    try:
        activities = garmin.get_activities(0, 50)
        print(f"Found {len(activities)} total activities")
    except Exception as e:
        print(f"❌ Failed to fetch activities: {e}")
        return
    
    # DEBUG: Print out the raw activityType for everything fetched
    for i, act in enumerate(activities):
        print(f"DEBUG Activity {i+1} Name: '{act.get('activityName')}' | Type Object: {act.get('activityType')}")
    
       # Filter for cycling activities using correct Garmin typeKeys
    cycling_activities = [
        activity for activity in activities 
        if activity.get('activityType', {}).get('typeKey', '').lower() in [
            'road_biking', 'road_cycling', 'cycling', 'gravel_unpaved_cycling', 
            'mountain_biking', 'indoor_cycling', 'virtual_cycling', 'biking'
        ]
    ]

    print(f"Found {len(cycling_activities)} cycling activities")
    
    if not cycling_activities:
        print("No cycling activities found in recent data")
        return
    
    # Connect to Google Sheets using SHEET_ID
    print("Connecting to Google Sheets...")
    try:
        creds_dict = json.loads(google_creds_json)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1
        print("✅ Connected to Google Sheets")
    except Exception as e:
        print(f"❌ Failed to connect to Google Sheets: {e}")
        return
    
    # Get existing dates to avoid duplicates
    try:
        existing_data = sheet.get_all_values()
        existing_dates = set()
        if len(existing_data) > 1:
            for row in existing_data[1:]:
                if row and row[0]:
                    existing_dates.add(row[0])
        print(f"Found {len(existing_dates)} existing entries")
    except Exception as e:
        print(f"Warning: Could not check existing data: {e}")
        existing_dates = set()
    
    # Process each cycling activity
    new_entries = 0
    for activity in cycling_activities:
        try:
            activity_date = activity.get('startTimeLocal', '')[:10]
            
            if activity_date in existing_dates:
                print(f"Skipping {activity_date} - already exists")
                continue
            
            activity_name = activity.get('activityName', 'Ride')
            distance_meters = activity.get('distance', 0)
            distance_miles = round(distance_meters / 1609.34, 2) if distance_meters else 0
            duration_seconds = activity.get('duration', 0)
            duration_min = format_duration(duration_seconds)
            avg_speed = format_speed(distance_meters, duration_seconds)
            avg_hr = activity.get('averageHR', 0) or 0
            max_hr = activity.get('maxHR', 0) or 0
            calories = activity.get('calories', 0) or 0
            avg_cadence = activity.get('averageBikingCadenceInRevPerMinute', 0) or 0
            elevation_gain = round(activity.get('elevationGain', 0) * 3.28084, 1) if activity.get('elevationGain') else 0
            activity_type = activity.get('activityType', {}).get('typeKey', 'cycling')
            avg_respiration = activity.get('averageRespiration', 0) or 0
            avg_temp_c = activity.get('averageTemperature')
            avg_temp_f = round(avg_temp_c * 9/5 + 32, 1) if avg_temp_c is not None else 0

            
            row = [
                activity_date,
                activity_name,
                distance_miles,
                duration_min,
                avg_speed,
                avg_hr,
                max_hr,
                calories,
                avg_cadence,
                elevation_gain,
                avg_respiration,
                avg_temp_f,
                activity_type
            ]
            
            sheet.append_row(row)
            print(f"✅ Added: {activity_date} - {activity_name} ({distance_miles} mi)")
            new_entries += 1
            
        except Exception as e:
            print(f"❌ Error processing activity: {e}")
            continue
    
    if new_entries > 0:
        print(f"\n🎉 Successfully added {new_entries} new cycling activities!")
    else:
        print("\n✓ No new activities to add")

if __name__ == "__main__":
    main()
