
#!/bin/sh

# Start the cron daemon in the background
cron &

# Execute the Python script
python /app/scraper.py
