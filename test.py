from datetime import datetime

now = datetime.now()

then = "2035-05-21 21:30:00"

format = "%Y-%m-%d %H:%M:%S"
dt_object = datetime.strptime(then, format)

print(now > dt_object)
print(dt_object)