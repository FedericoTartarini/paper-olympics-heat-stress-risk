from pythermalcomfort.models import solar_gain
from pvlib import location
import pandas as pd
from pprint import pprint


def calculate_mrt(lat: float, lon: float, tz: str, time_stamp: str):

    site_location = location.Location(lat, lon, tz=tz, name=tz)

    # Create a DatetimeIndex for a specific day
    times = pd.date_range(start=time_stamp, freq='h', tz=site_location.tz, periods=1)
    solar_position = site_location.get_solarposition(times=times)

    # pprint(solar_position.elevation)

    # Calculate clear sky irradiance
    clearsky_data = site_location.get_clearsky(times)

    # print(clearsky_data)

    mrt_calculation = {
        "wind_coefficient": 0.3,
        "sharp": 0,
        "sol_transmittance": 1,
        "f_svv": 1,
        "f_bes": 1,
        "asw": 0.7,
        "posture": "standing",
        "floor_reflectance": 0.1,
    }

    if solar_position["elevation"].values[0] < 0:
        msg = f"The sun is below the horizon at {time_stamp} for lat: {lat}, lon: {lon}. MRT calculation skipped."
        raise ValueError(msg)

    results = solar_gain(
        solar_position["elevation"].values[0],
        mrt_calculation["sharp"],
        clearsky_data["dni"].values[0],
        mrt_calculation["sol_transmittance"],
        mrt_calculation["f_svv"],
        mrt_calculation["f_bes"],
        mrt_calculation["asw"],
        mrt_calculation["posture"],
        mrt_calculation["floor_reflectance"],
    )

    print(f"MRT Results for {time_stamp} at lat: {lat}, lon: {lon}, dni: {clearsky_data['dni'].values[0]:.2f}")
    pprint(f"{results.delta_mrt=}")
    return results.delta_mrt

if __name__ == "__main__":
    lat = 52.5200
    lon = 13.4050
    tz = "Europe/Berlin"
    time_stamp = "2024-06-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)
    time_stamp = "2024-02-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)

    lat = -33.8688
    lon = 151.2093
    tz = "Australia/Sydney"
    time_stamp = "2024-06-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)

    time_stamp = "2024-02-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)

    lat = 1.3521
    lon = 103.8198
    tz = "Asia/Singapore"
    time_stamp = "2024-06-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)
    time_stamp = "2024-02-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)

    lat = 64.1466
    lon = -21.9426
    tz = "Atlantic/Reykjavik"
    time_stamp = "2024-06-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)
    time_stamp = "2024-02-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)
