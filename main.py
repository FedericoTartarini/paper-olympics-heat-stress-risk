from itertools import product

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pythermalcomfort.utilities import mean_radiant_tmp

from risk_calculation.mrt_calculation import calculate_mrt
from risk_calculation.comparison_old_new import get_sports_heat_stress_curves, sports_dict

def calculate_risk_value(lat: float, lon: float, tz: str, time_stamp: str, tdb: float, rh: float, sport_id: str):
    delta_mrt = calculate_mrt(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp)
    print(f"MRT: {delta_mrt+tdb:.2f} °C")
    wind_speed = sports_dict[sport_id]["wind_low"]
    print(f"tg =10 equal to MRT of {mean_radiant_tmp(tdb, 10, wind_speed):.2f} °C")
    risk = get_sports_heat_stress_curves(
        tdb=tdb,
        rh=rh,
        tr=tdb+delta_mrt,
        sport_id=sport_id,
        v=wind_speed
    )

    return risk


if __name__ == "__main__":
    lat = -33.8688
    lon = 151.2093
    tz = "Australia/Sydney"
    time_stamp = "2024-02-01 15:00:00"
    tdb = 37.0  # Dry-bulb temperature in °C
    rh = 50.0   # Relative humidity in %
    sport_id = "running"

    risk_value = calculate_risk_value(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, tdb=tdb, rh=rh, sport_id=sport_id)
    print(f"Calculated risk value: {risk_value}")


    results = []
    for t, rh in product(range(23, 50, 2), range(0, 101, 5)):
        risk_value = calculate_risk_value(lat=lat, lon=lon, tz=tz, time_stamp=time_stamp, tdb=t, rh=rh, sport_id=sport_id)
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


