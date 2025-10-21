from dataclasses import dataclass

import numpy as np
import pandas as pd

df_risk_parquet = pd.read_parquet("./risk_calculation/risk_reference_table.parquet")


sports_dict = {
    "abseiling": {
        "clo": 0.6,
        "met": 6.0,
        "sport_cat": 5,
        "wind_low": 0.5,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 120,
        "sport": "Abseiling",
    },
    "archery": {
        "clo": 0.75,
        "met": 4.5,
        "sport_cat": 1,
        "wind_low": 0.5,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 180,
        "sport": "Archery",
    },
    "australian_football": {
        "clo": 0.47,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 45,
        "sport": "Australian football",
    },
    "baseball": {
        "clo": 0.7,
        "met": 6.0,
        "sport_cat": 5,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 120,
        "sport": "Baseball",
    },
    "basketball": {
        "clo": 0.37,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 45,
        "sport": "Basketball",
    },
    "bowls": {
        "clo": 0.5,
        "met": 5.0,
        "sport_cat": 2,
        "wind_low": 0.5,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 180,
        "sport": "Bowls",
    },
    "canoeing": {
        "clo": 0.6,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 2.0,
        "wind_med": 2.5,
        "wind_high": 3,
        "duration": 60,
        "sport": "Canoeing",
    },
    "cricket": {
        "clo": 0.7,
        "met": 6.0,
        "sport_cat": 5,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 120,
        "sport": "Cricket",
    },
    "cycling": {
        "clo": 0.4,
        "met": 7.0,
        "sport_cat": 3,
        "wind_low": 3.0,
        "wind_med": 4.0,
        "wind_high": 5,
        "duration": 60,
        "sport": "Cycling",
    },
    "equestrian": {
        "clo": 0.9,
        "met": 7.4,
        "sport_cat": 4,
        "wind_low": 3.0,
        "wind_med": 3.5,
        "wind_high": 4,
        "duration": 60,
        "sport": "Equestrian",
    },
    "field_athletics": {
        "clo": 0.3,
        "met": 7.0,
        "sport_cat": 2,
        "wind_low": 1.0,
        "wind_med": 2.0,
        "wind_high": 3,
        "duration": 60,
        "sport": "Running (Athletics)",
    },
    "field_hockey": {
        "clo": 0.6,
        "met": 7.4,
        "sport_cat": 4,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 45,
        "sport": "Field hockey",
    },
    "fishing": {
        "clo": 0.9,
        "met": 4.0,
        "sport_cat": 1,
        "wind_low": 0.5,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 180,
        "sport": "Fishing",
    },
    "golf": {
        "clo": 0.5,
        "met": 5.0,
        "sport_cat": 1,
        "wind_low": 0.5,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 180,
        "sport": "Golf",
    },
    "horseback": {
        "clo": 0.9,
        "met": 7.4,
        "sport_cat": 4,
        "wind_low": 3.0,
        "wind_med": 3.5,
        "wind_high": 4,
        "duration": 60,
        "sport": "Horseback riding",
    },
    "kayaking": {
        "clo": 0.6,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 2.0,
        "wind_med": 2.5,
        "wind_high": 3,
        "duration": 60,
        "sport": "Kayaking",
    },
    "running": {
        "clo": 0.37,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 2.0,
        "wind_med": 2.5,
        "wind_high": 3,
        "duration": 60,
        "sport": "Long distance running",
    },
    "mtb": {
        "clo": 0.55,
        "met": 7.5,
        "sport_cat": 4,
        "wind_low": 3.0,
        "wind_med": 5.0,
        "wind_high": 5,
        "duration": 60,
        "sport": "Mountain biking",
    },
    "netball": {
        "clo": 0.37,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 45,
        "sport": "Netball",
    },
    "oztag": {
        "clo": 0.4,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 45,
        "sport": "Oztag",
    },
    "pickleball": {
        "clo": 0.4,
        "met": 6.5,
        "sport_cat": 3,
        "wind_low": 0.5,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 60,
        "sport": "Pickleball",
    },
    "climbing": {
        "clo": 0.6,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 1.0,
        "wind_med": 2.0,
        "wind_high": 3,
        "duration": 45,
        "sport": "Rock climbing",
    },
    "rowing": {
        "clo": 0.4,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 2.0,
        "wind_med": 2.5,
        "wind_high": 3,
        "duration": 60,
        "sport": "Rowing",
    },
    "rugby_league": {
        "clo": 0.47,
        "met": 7.5,
        "sport_cat": 4,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 45,
        "sport": "Rugby league",
    },
    "rugby_union": {
        "clo": 0.47,
        "met": 7.5,
        "sport_cat": 4,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 45,
        "sport": "Rugby union",
    },
    "sailing": {
        "clo": 1.0,
        "met": 6.5,
        "sport_cat": 5,
        "wind_low": 2.0,
        "wind_med": 2.5,
        "wind_high": 3,
        "duration": 180,
        "sport": "Sailing",
    },
    "shooting": {
        "clo": 0.6,
        "met": 5.0,
        "sport_cat": 1,
        "wind_low": 0.5,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 120,
        "sport": "Shooting",
    },
    "soccer": {
        "clo": 0.47,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 1.0,
        "wind_med": 2.0,
        "wind_high": 3,
        "duration": 45,
        "sport": "Soccer",
    },
    "softball": {
        "clo": 0.9,
        "met": 6.1,
        "sport_cat": 5,
        "wind_low": 1.0,
        "wind_med": 2.0,
        "wind_high": 3,
        "duration": 120,
        "sport": "Softball",
    },
    "tennis": {
        "clo": 0.4,
        "met": 7.0,
        "sport_cat": 3,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 60,
        "sport": "Tennis",
    },
    "touch": {
        "clo": 0.4,
        "met": 7.5,
        "sport_cat": 3,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 45,
        "sport": "Touch football",
    },
    "volleyball": {
        "clo": 0.37,
        "met": 6.8,
        "sport_cat": 3,
        "wind_low": 0.75,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 60,
        "sport": "Volleyball",
    },
    "walking": {
        "clo": 0.5,
        "met": 5.0,
        "sport_cat": 1,
        "wind_low": 0.5,
        "wind_med": 1.5,
        "wind_high": 3,
        "duration": 180,
        "sport": "Brisk walking",
    },
}


@dataclass
class Sport:
    clo: float
    met: float
    sport_cat: int
    wind_low: float
    wind_med: float
    wind_high: float
    duration: int
    sport: str


def calculate_comfort_indices_v2(data_for, sport_id):
    array_risk_results = []

    sport_dict = sports_dict[sport_id]
    sport = Sport(
        clo=sport_dict["clo"],
        met=sport_dict["met"],
        sport_cat=sport_dict["sport_cat"],
        wind_low=sport_dict["wind_low"],
        wind_med=sport_dict["wind_med"],
        wind_high=sport_dict["wind_high"],
        duration=sport_dict["duration"],
        sport=sport_dict["sport"],
    )

    # data_for = data_for.resample("60min").interpolate()
    for ix, row in data_for.iterrows():
        tdb = row["tdb"]
        tg = row["tg"]
        rh = row["rh"]
        wind_speed = row["v"]

        if tg < 4:
            tg = 4
        elif tg > 12:
            tg = 12
        tg = round(tg)

        if wind_speed < sport.wind_low:
            wind_speed = sport.wind_low
        elif wind_speed > sport.wind_high - 0.5:
            wind_speed = sport.wind_high - 0.5
        wind_speed = round(round(wind_speed / 0.5) * 0.5, 2)

        if tdb < 24:
            tdb = 24
        elif tdb > 43.5:
            tdb = 43.5
        tdb = round(tdb * 2) / 2

        if rh < 0:
            rh = 0
        elif rh > 99:
            rh = 99
        rh = round(rh)

        try:
            risk_value = df_risk_parquet.loc[(tdb, rh, tg, wind_speed, sport_id)]
            risk_value = risk_value.to_dict()
        except KeyError as e:
            print(
                f"Parquet file - Risk value not found for {tdb=}, {rh=}, {tg=}, {wind_speed=}, {sport_id=}: {e}"
            )
            risk_value = {
                "risk": None,
                "rh_threshold_moderate": None,
                "rh_threshold_high": None,
                "rh_threshold_extreme": None,
            }

        top = 100
        if risk_value["rh_threshold_extreme"] > top:
            top = risk_value["rh_threshold_extreme"] + 10

        x = [
            0,
            risk_value["rh_threshold_moderate"],
            risk_value["rh_threshold_high"],
            risk_value["rh_threshold_extreme"],
            top,
        ]
        y = np.arange(0, 5, 1)

        risk_value_interp = np.around(np.interp(row["rh"], x, y), 1)

        if row["tdb"] < 20:
            risk_value_interp *= 0
        elif row["tdb"] < 21:
            risk_value_interp *= 0.2
        elif row["tdb"] < 22:
            risk_value_interp *= 0.4
        elif row["tdb"] < 23:
            risk_value_interp *= 0.6
        elif row["tdb"] < 24:
            risk_value_interp *= 0.8
        risk_value_interp = round(risk_value_interp, 2)

        array_risk_results.append([risk_value["risk"], risk_value_interp])

    data_for[["risk_value", "risk_value_interpolated"]] = array_risk_results

    risk_value = {0: "low", 1: "moderate", 2: "high", 3: "extreme"}
    data_for["risk"] = data_for["risk_value"].map(risk_value)

    return data_for
