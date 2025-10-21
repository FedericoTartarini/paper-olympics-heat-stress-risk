from itertools import product

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from cachetools import cached, TTLCache

from risk_calculation.mrt_calculation import calculate_mrt
from risk_calculation.new_risk_eq_v2 import (
    get_sports_heat_stress_curves,
    sports_dict,
)


@cached(cache=TTLCache(maxsize=1000, ttl=600))
def calculate_risk_value(
    lat: float,
    lon: float,
    tz: str,
    time_stamp: str,
    tdb: float,
    rh: float,
    sport_id: str,
    wind: str = "low",
):
    """
    Calculate the heat-stress risk value for a sport at a specific location and local time.

    This function combines environmental inputs (dry-bulb temperature and relative humidity)
    with radiant effects estimated by calculate_mrt to compute a sport-specific risk using
    the project's sports heat-stress curve logic.

    Parameters
    ----------
    lat : float
        Latitude in decimal degrees (north positive, south negative).
    lon : float
        Longitude in decimal degrees (east positive, west negative).
    tz : str
        Time zone identifier compatible with zoneinfo/pytz (e.g., "Europe/Berlin").
    time_stamp : str
        Local date/time string parseable by pandas (e.g., "2024-06-01 15:00:00").
    tdb : float
        Dry-bulb air temperature in degrees Celsius.
    rh : float
        Relative humidity as a percentage (0-100).
    sport_id : str
        Identifier for the sport; must correspond to an entry in the project's sports_dict
        or equivalent lookup used by get_sports_heat_stress_curves.
    wind : str, optional
        Wind category key (e.g., "low", "med", "high") used to select wind speed assumptions.
        Default is "low".

    Returns
    -------
    float
        Numeric risk value as defined by get_sports_heat_stress_curves. Interpretation of the
        returned value (e.g., discrete risk levels or continuous severity score) depends on
        that function's implementation.

    Raises
    ------
    KeyError
        If sport_id or expected wind keys are missing from the sports configuration.
    ValueError
        If input ranges are invalid (e.g., rh outside 0-100) or time_stamp cannot be parsed.
    Exception
        Propagates exceptions from calculate_mrt, get_sports_heat_stress_curves, or underlying libraries.

    Notes
    -----
    - The function calls calculate_mrt to obtain delta_mrt and combines it with tdb to form
      an operative/radiant temperature used by the sport-specific risk curve.
    - Results may be cached (depending on function decorators) to speed repeated identical calls.
    - Adjust sport configuration or wind-category mapping if you need different assumptions.

    Examples
    --------
    >>> calculate_risk_value(52.52, 13.405, "Europe/Berlin", "2024-06-01 15:00:00",
    ...                      tdb=30.0, rh=60.0, sport_id="soccer", wind="low")
    2.0
    """
    delta_mrt = calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)
    print(f"MRT: {delta_mrt + tdb:.2f} °C")
    wind_speed = sports_dict[sport_id][f"wind_{wind}"]
    # print(f"tg =10 equal to MRT of {mean_radiant_tmp(tdb, 10, wind_speed):.2f} °C")
    risk = get_sports_heat_stress_curves(
        tdb=tdb, rh=rh, tr=tdb + delta_mrt, sport_id=sport_id, v=wind_speed
    )

    return risk


def check_calculate_risk_value(
    lat: float,
    lon: float,
    tz: str,
    time_stamp: str,
    tdb: float,
    rh: float,
    sport_id: str,
    wind: str = "low",
):
    risk_value = calculate_risk_value(
        lat=lat,
        lon=lon,
        tz=tz,
        time_stamp=time_stamp,
        tdb=tdb,
        rh=rh,
        sport_id=sport_id,
        wind=wind,
    )
    print(f"Risk Value: {risk_value}")


def check_calculate_risk_value_grid(
    lat: float,
    lon: float,
    tz: str,
    time_stamp: str,
    sport_id: str,
    wind: str = "low",
):
    results = []
    for t, rh in product(range(23, 50, 2), range(0, 101, 5)):
        risk_value = calculate_risk_value(
            lat=lat,
            lon=lon,
            tz=tz,
            time_stamp=time_stamp,
            tdb=t,
            rh=rh,
            sport_id=sport_id,
            wind=wind,
        )
        results.append([t, rh, risk_value])

    df_new = pd.DataFrame(results, columns=["tdb", "rh", "risk"])

    f, ax = plt.subplots(figsize=(10, 8))
    df_pivot = df_new.pivot(index="rh", columns="tdb", values="risk")
    df_pivot.sort_index(ascending=False, inplace=True)
    sns.heatmap(df_pivot, annot=False, cmap="viridis", ax=ax, vmin=0, vmax=3)
    ax.set_title(f"Heat Stress Risk for {sport_id} at {time_stamp} in Sydney")
    ax.set_xlabel("Dry-Bulb Temperature (°C)")
    ax.set_ylabel("Relative Humidity (%)")
    plt.show()


if __name__ == "__main__":
    check_calculate_risk_value(
        lat=-33.8688,
        lon=151.2093,
        tz="Australia/Sydney",
        time_stamp="2024-02-01 15:00:00",
        tdb=30.0,
        rh=60.0,
        sport_id="soccer",
    )

    check_calculate_risk_value_grid(
        lat=-33.8688,
        lon=151.2093,
        tz="Australia/Sydney",
        time_stamp="2024-02-01 12:00:00",
        sport_id="basketball",
        wind="high",  # "high", "med", or "low"
    )
