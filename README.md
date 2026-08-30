# 🚴 Garmin Cycling Data to Google Sheets Sync README

Automatically syncs Garmin Connect Cycling data to Google Sheets, runs daily.

# What this project does?

* Fetches your last 10 activities from Garmin Connect
* Filters for cycling activities only
* Extracts key running metrics:

    - Distance in miles
    - Duration in minutes
    - Average pace (mph)
    - Average and max heart rate
    - Calories burned
    - Average cadence (cycles per minute)
    - Elevation gain (ft)
    - Average respiration rate per minute
    - Temperature in fahrenheit
    - Aerobic training effect
    - Anaerobic training effect
    - Heart rate minutes per zone (1-5)
    - Activity type

* Avoids duplicates by checking existing dates in your sheet
* Appends new activity to your Google Sheet
* Runs daily, automatically

# Want to sync more activities? 
Change line:
```
activities = garmin.get_activities(0, 10)  # Increase this number
```
# Google Sheet Instructions

* Create Google Sheet
* Go to Google Sheets
* Create a new sheet called "Garmin Data"
* Add headers in row 1 (copy/paste below)
    ```
    Date	Activity Name	Distance (miles)	Duration (min)	Avg Speed (mph)	Avg HR	Max HR	Calories	Avg Cadence	Elevation Gain (ft)	Avg Respiration	Temperature (°F)	Aerobic Training Effect	Anaerobic Training Effect	Zone 1 HR (min)	Zone 2 HR (min)	Zone 3 HR (min)	Zone 4 HR (min)	Zone 5 HR (min)	Activity Type
    ```
* If you're testing locally, then share and give editor access to your Google Cloud Service Account.

# Set Up Google Cloud Credentials

* Go to Google Cloud Console
* Create a new project (or use existing)
* Enable Google Sheets API:

    - Click "Enable APIs and Services"
    - Search "Google Sheets API"
    - Click Enable

* Enable Google Drive API
* Create Service Account:

    - Go to "IAM & Admin" → "Service Accounts"
    - Click "Create Service Account"
    - Name it "garmin-gsheets-cycling-sync" → Click Create
    - Skip optional steps → Click Done

* Create Key:

    - Click on the service account you just created
    - Go to "Keys" tab
    - "Add Key" → "Create new key" → JSON
    - Save the JSON file (you'll need this!)

* Share your Google Sheet:

    - Open your "Garmin Data" sheet
    - Click Share
    - Add the service account email (looks like garmin-gsheets-cycling-sync@your-project.iam.- gserviceaccount.com)
    - Give it "Editor" access

* Push to github
```
cd garmin-gsheets—cycling-sync
git init
git add .
git commit -m "Initial commit"
git branch -M main
```
* On GitHub:

    - Create a new repository called "garmin-gsheets-cycling-sync"
    - Follow GitHub's instructions to push:

* Add GitHub Secrets

    - Go to your GitHub repository
    - Click Settings → Secrets and variables → Actions
    - Click New repository secret and add these four secrets:

* Secret 1: GARMIN_EMAIL
```
Name: GARMIN_EMAIL
Value: Your Garmin Connect email
```

* Secret 2: GARMIN_PASSWORD
```
Name: GARMIN_PASSWORD
Value: Your Garmin Connect password
```

* Secret 3: GOOGLE_CREDENTIALS
```
Name: GOOGLE_CREDENTIALS
Value: The entire contents of the JSON file you downloaded (copy & paste everything)
```

* Secret 4: SHEETS_ID
```
Name: SHEETS_ID
Value: The unique ID number in your Garmin Data Google sheets, you can find it in the URL
    https://docs.google.com/spreadsheets/d/[SHEETS_ID]/edit?gid=379328079
```

* Test It!

    - Go to your repository
    - Click Actions tab
    - Click on "Garmin to Google Sheets Sync" workflow
    - Click Run workflow → Run workflow (green button)
    - Watch it run! Click on the running job to see logs
    - Check your Google Sheet - you should see data appear!

* Verify Scheduling
    * The workflow is set to run automatically every day at 6 AM UTC. You can:

    - Change the cron schedule in garmin-sync.yml
    - Run manually anytime using "Run workflow" button
    - Check the Actions tab to see run history

# Testing Locally

* In your project, create a .env file, add it to .gitignore and add with your own credentials:
```
GARMIN_EMAIL=your@mail.com
GARMIN_PASSWORD=yourpasswords
SHEET_ID=get from Gsheets URL
GOOGLE_CREDENTIALS={"type": "service_account","project_id": ...}
```
# Future improvements
* Add more activities
