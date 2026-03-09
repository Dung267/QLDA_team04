from celery import shared_task

@shared_task
def sync_weather_for_all_areas():
    # duyệt theo Area
    # gọi OpenWeather
    # validate dữ liệu
    # lưu WeatherSnapshot
    pass