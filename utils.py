from datetime import datetime, timedelta

def is_within_3_hours(input_datetime):
    generation_date = datetime.strptime(input_datetime, "%Y-%m-%d %H:%M:%S")
    current_datetime = datetime.now()
    time_difference = current_datetime - generation_date
    print(time_difference)

    if time_difference > timedelta(minutes=180):
        return False
    else:
        return True
