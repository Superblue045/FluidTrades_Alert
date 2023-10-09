from datetime import datetime

# Assuming timestamp_seconds contains the timestamp in seconds
timestamp_seconds = 1695129000

# Convert timestamp to a datetime object
timestamp_datetime = datetime.utcfromtimestamp(timestamp_seconds)

# Format the datetime object as a string (you can change the format as needed)
formatted_date = timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')

print(formatted_date)