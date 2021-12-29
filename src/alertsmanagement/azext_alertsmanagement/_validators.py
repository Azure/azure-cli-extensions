import datetime

def validate_date_format(namespace):
    if namespace.schedule_start_date:
        format = '%m/%d/%Y'
        datetime.datetime.strptime(namespace.schedule_start_date[0], format)