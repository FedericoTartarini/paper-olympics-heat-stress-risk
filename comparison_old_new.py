from dataclasses import dataclass
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import seaborn as sns

from pythermalcomfort.models import phs
from pythermalcomfort.utilities import mean_radiant_tmp

df_risk_parquet = pd.read_parquet("risk_reference_table.parquet")

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


def get_sports_heat_stress_curves(
    tdb, tg, rh, v=0.8, clo=None, met=None, sport_id="soccer", sweat_loss_g=850
):
    sport_dict = sports_dict[sport_id]

    max_t_low = 34.5
    max_t_medium = 39
    max_t_high = 43.5
    min_t_extreme = 26
    min_t_high = 25
    min_t_medium = 23

    if tdb < min_t_medium:
        return 0
    if tdb > max_t_high:
        return 3

    t_cr_extreme = 40

    if clo is None:
        clo = sport_dict["clo"]
    if met is None:
        met = sport_dict["met"]

    if v < sport_dict["wind_low"]:
        v = sport_dict["wind_low"]
    elif v > sport_dict["wind_high"]:
        v = sport_dict["wind_high"]

    tr = mean_radiant_tmp(tdb=tdb, tg=tg, v=v)

    def calculate_threshold_water_loss(x):
        return (
            phs(
                tdb=x,
                tr=tr,
                v=v,
                rh=rh,
                met=met,
                clo=clo,
                posture="standing",
                duration=sport_dict["duration"],
                # duration=60,
                round=False,
                limit_inputs=False,
                acclimatized=100,
                i_mst=0.4,
            )["sweat_loss_g"]
            / sport_dict["duration"]
            * 45
            - sweat_loss_g
        )

    for min_t, max_t in [(0, 36), (20, 50)]:
        try:
            t_medium = scipy.optimize.brentq(
                calculate_threshold_water_loss, min_t, max_t
            )
            break
        except ValueError as e:
            print(f"Water loss - Brentq failed for {tdb=} and {rh=}: {e}")
            t_medium = max_t_low

    def calculate_threshold_core(x):
        return (
            phs(
                tdb=x,
                tr=tr,
                v=v,
                rh=rh,
                met=met,
                clo=clo,
                posture="standing",
                duration=sport_dict["duration"],
                round=False,
                limit_inputs=False,
                acclimatized=100,
                i_mst=0.4,
            )["t_cr"]
            - t_cr_extreme
        )

    for min_t, max_t in [(0, 36), (20, 50)]:
        try:
            t_extreme = scipy.optimize.brentq(calculate_threshold_core, min_t, max_t)
            break
        except ValueError as e:
            print(f"Core temp - Brentq failed for {tdb=} and {rh=}: {e}")
            t_extreme = max_t_high

    t_high = (
        (t_medium + t_extreme) / 2
        if not (np.isnan(t_medium) or np.isnan(t_extreme))
        else np.nan
    )
    risk_level = np.nan

    if t_medium > max_t_low:
        t_medium = max_t_low
    if t_high > max_t_medium:
        t_high = max_t_medium
    if t_extreme > max_t_high:
        t_extreme = max_t_high

    if t_extreme < min_t_extreme:
        t_extreme = min_t_extreme
    if t_high < min_t_high:
        t_high = min_t_high
    if t_medium < min_t_medium:
        t_medium = min_t_medium

    if tdb < t_medium:
        risk_level = 0
    elif t_medium <= tdb < t_high:
        risk_level = 1
    elif t_high <= tdb < t_extreme:
        risk_level = 2
    elif tdb >= t_extreme:
        risk_level = 3

    if np.isnan(risk_level):
        raise ValueError("Risk level could not be determined due to NaN thresholds.")

    return risk_level


if __name__ == "__main__":
    # get the lowest wind speed across all sports
    min_wind_speed = max(
        [sports_dict[sport]["wind_low"] for sport in sports_dict.keys()]
    )
    print(f"Minimum wind speed across all sports: {min_wind_speed} m/s")
    max_wind_speed = min(
        [sports_dict[sport]["wind_high"] for sport in sports_dict.keys()]
    )
    print(f"Maximum wind speed across all sports: {max_wind_speed} m/s")

    for sport in sports_dict.keys():
        # sport = "softball"
        tg_delta = 10  # tg - tdb
        sweat_loss_g = 825  # 825 g per hour
        v = sports_dict[sport]["wind_low"]

        results = []

        for t, rh in product(range(23, 50, 2), range(0, 101, 5)):
            print(f"Calculating for {sport=} {t=} {rh=} {v=}")
            tg = tg_delta + t
            risk = get_sports_heat_stress_curves(
                tdb=t, tg=tg, rh=rh, v=v, sport_id=sport, sweat_loss_g=sweat_loss_g
            )
            results.append([t, rh, tg_delta, v, risk])

        df_new = pd.DataFrame(results, columns=["tdb", "rh", "tg", "v", "risk"])

        df_sma = calculate_comfort_indices_v2(data_for=df_new.copy(), sport_id=sport)

        # plot side by side heatmaps
        f, axs = plt.subplots(3, 1, figsize=(7, 7), sharex=True, sharey=True)

        df_pivot = df_new.pivot(index="rh", columns="tdb", values="risk")
        df_pivot.sort_index(ascending=False, inplace=True)
        sns.heatmap(df_pivot, annot=False, cmap="viridis", ax=axs[0], vmin=0, vmax=3)

        df_pivot_sma = df_sma.pivot(index="rh", columns="tdb", values="risk_value")
        df_pivot_sma.sort_index(ascending=False, inplace=True)
        sns.heatmap(
            df_pivot_sma, annot=False, cmap="viridis", ax=axs[1], vmin=0, vmax=3
        )

        df_new["diff"] = df_sma["risk_value"] - df_new["risk"]
        df_diff_pivot = df_new.pivot(index="rh", columns="tdb", values="diff")
        df_diff_pivot.sort_index(ascending=False, inplace=True)
        sns.heatmap(
            df_diff_pivot,
            annot=False,
            center=0,
            cmap="coolwarm",
            ax=axs[2],
            vmin=-3,
            vmax=3,
        )

        axs[0].set_title(
            f"{sports_dict[sport]['sport']} - Heat stress risk (PHS model)", fontsize=14
        )
        axs[1].set_title(
            f"{sports_dict[sport]['sport']} - Heat stress risk (SMA model)", fontsize=14
        )
        axs[2].set_title(
            f"{sports_dict[sport]['sport']} - Difference in risk levels (SMA -PHS)",
            fontsize=14,
        )
        axs[0].set_ylabel("Relative Humidity (%)", fontsize=12)
        axs[1].set_ylabel("Relative Humidity (%)", fontsize=12)
        axs[2].set_ylabel("Relative Humidity (%)", fontsize=12)
        axs[0].set_xlabel("Air Temperature (°C)", fontsize=12)
        axs[1].set_xlabel("Air Temperature (°C)", fontsize=12)
        axs[2].set_xlabel("Air Temperature (°C)", fontsize=12)
        plt.tight_layout()
        plt.savefig(
            f"./figures/{sport}_v={v}_tg_delta={tg_delta}.png",
            dpi=300,
        )
        plt.show()

    t = 50
    tr = mean_radiant_tmp(tg=t + tg_delta, tdb=t, v=v)
    rh = 0
    print(
        phs(
            tdb=t,
            tr=tr,
            v=v,
            rh=rh,
            met=sports_dict[sport]["met"],
            clo=sports_dict[sport]["clo"],
            posture="standing",
            duration=sports_dict[sport]["duration"],
            round=True,
            limit_inputs=False,
            acclimatized=100,
            i_mst=0.4,
        )
    )

    # def calculate_threshold_water_loss(x):
    #     return (
    #         phs(
    #             tdb=x,
    #             tr=tr,
    #             v=v,
    #             rh=rh,
    #             met=sports_dict[sport]["met"],
    #             clo=sports_dict[sport]["clo"],
    #             posture="standing",
    #             duration=sports_dict[sport]["duration"],
    #             round=True,
    #             limit_inputs=False,
    #             acclimatized=100,
    #             i_mst=0.4,
    #         )["sweat_loss_g"]
    #         - sweat_loss_g
    #     )
    #
    # try:
    #     print(scipy.optimize.brentq(calculate_threshold_water_loss, 26, 34))
    # except ValueError as e:
    #     print(f"Water loss - Brentq failed for {t=} and {rh=}: {e}")
    #     t_medium = np.nan
    #
    # results = []
    # for t in range(20, 43, 1):
    #     for rh in range(0, 101, 1):
    #         tr = mean_radiant_tmp(tg=t+tg_delta, tdb=t, v=v)
    #         water_loss_g = phs(
    #             tdb=t,
    #             tr=tr,
    #             v=v,
    #             rh=rh,
    #             met=sports_dict[sport]["met"],
    #             clo=sports_dict[sport]["clo"],
    #             posture="standing",
    #             duration=sports_dict[sport]["duration"],
    #             round=True,
    #             limit_inputs=False,
    #             acclimatized=100,
    #             i_mst=0.4,
    #         )["sweat_loss_g"] / sports_dict[sport]["duration"] * 45
    #         results.append([t, rh, water_loss_g])
    # df_water_loss = pd.DataFrame(results, columns=["tdb", "rh", "water_loss_g"])
    # df_water_loss_pivot = df_water_loss.pivot(
    #     index="rh", columns="tdb", values="water_loss_g"
    # )
    # df_water_loss_pivot.sort_index(ascending=False, inplace=True)
    # plt.figure(figsize=(7, 5))
    # sns.heatmap(df_water_loss_pivot, annot=False, cmap="viridis", vmin=sweat_loss_g-100, vmax=sweat_loss_g+100)
    # plt.title(
    #     f"{sports_dict[sport]['sport']} - Sweat loss (g) for {sports_dict[sport]['duration']} min",
    #     fontsize=14,
    # )
    # plt.ylabel("Relative Humidity (%)", fontsize=12)
    # plt.xlabel("Air Temperature (°C)", fontsize=12)
    # plt.tight_layout()
    # plt.show()
