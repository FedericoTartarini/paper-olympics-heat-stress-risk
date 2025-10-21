from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import seaborn as sns
from cachetools import cached, TTLCache

from pythermalcomfort.models import phs
from pythermalcomfort.utilities import mean_radiant_tmp

from risk_calculation.sma_code_v2 import sports_dict, calculate_comfort_indices_v2


@cached(cache=TTLCache(maxsize=2000, ttl=3600))
def get_sports_heat_stress_curves(
    tdb,
    rh,
    v=0.8,
    tg=None,
    tr=None,
    clo=None,
    met=None,
    sport_id="soccer",
    sweat_loss_g=850,
):
    sport_dict = sports_dict[sport_id]

    if tg is not None and tr is None:
        tr = mean_radiant_tmp(tdb=tdb, tg=tg, v=v)
    if tg is None and tr is None:
        raise ValueError("Either tg or tr must be provided.")

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


def compare_sma_v2_with_new_risk_eq():
    for sport in sports_dict.keys():
        # sport = "softball"
        tg_delta = 4  # tg - tdb
        v = sports_dict[sport]["wind_low"]

        results = []

        for t, rh in product(range(23, 50, 2), range(0, 101, 5)):
            # print(f"Calculating for {sport=} {t=} {rh=} {v=}")
            tg = tg_delta + t
            risk = get_sports_heat_stress_curves(
                tdb=t, tg=tg, rh=rh, v=v, sport_id=sport
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


if __name__ == "__main__":
    compare_sma_v2_with_new_risk_eq()

    # # get the lowest wind speed across all sports
    # min_wind_speed = max(
    #     [sports_dict[sport]["wind_low"] for sport in sports_dict.keys()]
    # )
    # print(f"Minimum wind speed across all sports: {min_wind_speed} m/s")
    # max_wind_speed = min(
    #     [sports_dict[sport]["wind_high"] for sport in sports_dict.keys()]
    # )
    # print(f"Maximum wind speed across all sports: {max_wind_speed} m/s")

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
