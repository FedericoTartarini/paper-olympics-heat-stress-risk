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
    Calculate Mean Radiant Temperature (MRT) difference for a single local datetime.

    Uses pvlib to compute solar geometry and clear-sky irradiance and pythermalcomfort.models.solar_gain
    to estimate the mean radiant temperature difference (results.delta_mrt).

    Parameters
    ----------
    lat : float
        Latitude in decimal degrees (north positive, south negative).
    lon : float
        Longitude in decimal degrees (east positive, west negative).
    tz : str
        Time zone string compatible with zoneinfo/pytz (e.g. "Europe/Berlin").
    time_stamp : str
        Local date/time string parseable by pandas (e.g. "2024-06-01 15:00:00").
        A single timestamp is expected; the function constructs a single-period hourly DatetimeIndex.
    print_output : bool, optional
        If True, prints human-readable debug output via icecream.ic (default: False).

    Returns
    -------
    float
        The computed mean radiant temperature difference (delta_mrt) in degrees Celsius.
        If the sun is below the horizon at the requested time/location the function returns 0.

    Raises
    ------
    ValueError
        If provided latitude/longitude are outside reasonable bounds or time_stamp cannot be parsed.
    Exception
        Errors raised by pvlib, pandas, or pythermalcomfort are propagated to the caller.

    Notes
    -----
    - Results are cached using cachetools.cached with TTLCache(maxsize=1000, ttl=600) to avoid repeated expensive calculations.
    - The function uses clear-sky (get_clearsky) DNI for direct radiation; adjust parameters if measured irradiance is desired.
    - The function assumes a standing posture and default radiative parameters (asw, floor_reflectance, etc.).
    - The function performs a single-hour calculation (freq="h", periods=1).

    Examples
    --------
    >>> calculate_mrt(52.52, 13.405, "Europe/Berlin", "2024-06-01 15:00:00")
    5.23
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
    Measure the execution time of calculate_mrt for repeated invocations.

    Performs one warm-up call (to populate caches and perform lazy initialization), then
    invokes calculate_mrt `runs` times using fixed test parameters and reports elapsed time
    through icecream.ic.

    Parameters
    ----------
    runs : int, optional
        Number of times to call calculate_mrt (default: 1000). Large values will produce a longer measurement.

    Returns
    -------
    None
        Prints timing information (total elapsed time in seconds, rounded) via icecream.ic and returns None.

    Notes
    -----
    - This helper is intended for informal benchmarking. For rigorous profiling, use timeit or a profiler.
    - The current implementation uses hard-coded location/time values inside the function; modify the function
      if you want to benchmark different inputs or make it return measured values programmatically.

    Example
    -------
    >>> time_function(runs=10000)
    # prints the rounded total execution time in seconds via ic(...)
    """
    # time this function to see how long it takes to run 100_000 times
    lat = 52.5200
    lon = 13.4050
    tz = "Europe/Berlin"
    time_stamp = "2024-06-01 15:00:00"

    # Warm-up (loads modules, caches, etc.)
    try:
        calculate_mrt(
            lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=False
        )
    except Exception as e:
        ic(f"Warm-up call failed: {e}")

    start = time.perf_counter()
    for _ in range(runs):
        calculate_mrt(
            lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, print_output=False
        )
    end = time.perf_counter()

    total = end - start
    avg = total / runs if runs else float("nan")
    total_time_s = round(total, 2)
    # ic(f"Ran calculate_mrt {runs} times. Total time: {total:.4f} s. Avg per call: {avg*1000:.6f} ms.")
    ic(total_time_s)


if __name__ == "__main__":
    # test_few_locations()
    time_function(runs=1_000_000)
