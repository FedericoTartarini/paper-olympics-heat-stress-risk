from icecream import ic
from pythermalcomfort.models import solar_gain
from pvlib import location
import pandas as pd
import time
from cachetools import cached, TTLCache

ic.configureOutput(includeContext=True)

@cached(cache=TTLCache(maxsize=1000, ttl=600))
def calculate_mrt(
    lat: float, lon: float, tz: str, time_stamp: str, print_output: bool = False
) -> float:
    """
    Calculate Mean Radiant Temperature (MRT) based on location and time using pvlib and pythermalcomfort.

    :param lat: Latitude in decimal degrees (positive for north, negative for south).
    :param lon: Longitude in decimal degrees (positive for east, negative for west).
    :param tz: Timezone name compatible with `pytz`/`zoneinfo`, e.g. `Europe/Berlin`.
    :param time_stamp: Local date/time string parseable by `pandas`, e.g. `2024-06-01 15:00:00`.
    :param print_output: If `True`, prints debug output using `icecream.ic` (default: `False`).

    :return: `delta_mrt` (float) — Mean Radiant Temperature difference in °C. Returns `0` if sun is below horizon.
    """
    # Define the location
    site_location = location.Location(lat, lon, tz=tz, name=tz)

    # Create a DatetimeIndex for the specified time
    times = pd.date_range(start=time_stamp, freq="h", tz=site_location.tz, periods=1)

    # Get solar position
    solar_position = site_location.get_solarposition(times=times)

    # exit if sun is below horizon
    if solar_position["elevation"].values[0] < 0:
        msg = f"The sun is below the horizon at {time_stamp} for lat: {lat}, lon: {lon}. MRT calculation skipped."
        ic(msg)
        return 0

    # Calculate clear sky irradiance
    clear_sky_data = site_location.get_clearsky(times)

    results = solar_gain(
        sol_altitude=solar_position["elevation"].values[0],
        sharp=0,
        sol_radiation_dir=clear_sky_data["dni"].values[0],
        sol_transmittance=1,
        f_svv=1,
        f_bes=1,
        asw=0.7,
        posture="standing",
        floor_reflectance=0.1,
    )

    if print_output:
        ic(
            f"MRT Results for {time_stamp} at lat: {lat}, lon: {lon}, dni: {clear_sky_data['dni'].values[0]:.2f}"
        )
        ic(results)

    return results.delta_mrt


def test_few_locations():

    lat = 52.5200
    lon = 13.4050
    tz = "Europe/Berlin"
    time_stamp = "2024-06-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=True)
    time_stamp = "2024-02-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=True)

    lat = -33.8688
    lon = 151.2093
    tz = "Australia/Sydney"
    time_stamp = "2024-06-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=True)

    time_stamp = "2024-02-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=True)

    time_stamp = "2024-06-01 20:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=True)

    lat = 1.3521
    lon = 103.8198
    tz = "Asia/Singapore"
    time_stamp = "2024-06-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=True)
    time_stamp = "2024-02-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=True)

    lat = 64.1466
    lon = -21.9426
    tz = "Atlantic/Reykjavik"
    time_stamp = "2024-06-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)
    time_stamp = "2024-02-01 15:00:00"
    calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)


def time_function(runs: int = 1_000):
    """
    Time the calculate_mrt function over multiple runs to assess performance.
    """
    # time this function to see how long it takes to run 100_000 times
    lat = 52.5200
    lon = 13.4050
    tz = "Europe/Berlin"
    time_stamp = "2024-06-01 15:00:00"

    # Warm-up (loads modules, caches, etc.)
    try:
        calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=False)
    except Exception as e:
        ic(f"Warm-up call failed: {e}")

    start = time.perf_counter()
    for _ in range(runs):
        calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=False)
    end = time.perf_counter()

    total = end - start
    avg = total / runs if runs else float("nan")
    total_time_s = round(total, 2)
    # ic(f"Ran calculate_mrt {runs} times. Total time: {total:.4f} s. Avg per call: {avg*1000:.6f} ms.")
    ic(total_time_s)


if __name__ == "__main__":
    # test_few_locations()
    time_function(runs=1_000_000)