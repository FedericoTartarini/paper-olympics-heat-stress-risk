# Olympics Data Analysis - Heat Stress Risk Calculator

This repository contains a Python-based tool for calculating heat-stress risk values for various sports. It integrates environmental data such as dry-bulb temperature, relative humidity, with location and time data to to calculate risk levels for athletes.

The core functionality is provided by the `calculate_risk_value` function in the `main.py` file, which returns risk levels ranging from 0 (low risk) to 3 (high risk).

## Features

- **Mean Radiant Temperature (MRT) Calculation**: Estimates solar gain effects using pvlib and pythermalcomfort libraries based on geographic and temporal data. Please note that the MRT calculation is an approximation and it assumes clear sky conditions.
- **Sport-Specific Risk Assessment**: Supports multiple sports the full list of the sports can be found in the `sports_dict` in the `sma_code_v2.py` file. Please note that the sport names passed to the functions should match the keys in this dictionary.
- **Caching**: Optimized with TTLCache for repeated calculations to improve performance.
- **Visualization**: Includes tools to generate heatmaps of risk values across temperature and humidity ranges. See the `check_calculate_risk_value_grid` function for details in the `main.py` file.

## Installation

This project uses Pipenv for dependency management. Ensure you have Pipenv installed (`pip install pipenv`).

1. Clone the repository:
   ```bash
   git clone https://github.com/FedericoTartarini/paper-olympics-heat-stress-risk.git
   cd paper-olympics-heat-stress-risk
   ```

2. Install dependencies:
   ```bash
   pipenv install
   ```

3. Activate the virtual environment:
   ```bash
   pipenv shell
   ```

## Usage

### Using the `calculate_risk_value` Function

The main function is `calculate_risk_value` located in `main.py`. It calculates the heat-stress risk for a given sport at a specific location and time.

#### Parameters:
- `lat` (float): Latitude in decimal degrees.
- `lon` (float): Longitude in decimal degrees.
- `tz` (str): Time zone (e.g., "Australia/Sydney"). Time zone must be valid according to the [`pytz` library](https://pynative.com/list-all-timezones-in-python/#h-get-list-of-all-timezones-name)
- `time_stamp` (str): Local date/time string (e.g., "2024-02-01 15:00:00"). Please note that the year is not needed, hence you can always use "2024" as the year. However, the month, day, hour and minute should reflect the actual date and time of interest for the solar calculations. Please note that the script automatically calculates the solar elevation and if negative, it sets the MRT to be equal to the dry-bulb temperature, as there is no solar gain during nighttime.
- `tdb` (float): Dry-bulb air temperature in °C.
- `rh` (float): Relative humidity as a percentage (0-100).
- `sport_id` (str): Sport identifier (e.g., "soccer", "basketball", which are keys of the `sport_dict` file mentioned before).
- `wind` (str, optional): Wind category ("low", "med", "high"). Default is "low". This is used to estimate wind speed for the risk calculation. You can refer to the `sport_dict` in `sma_code_v2.py` for more details on how wind speed is categorized for each sport. If we use "low", the wind speed will be set to the minimum value defined for that sport, however, this may be a bit unrealistic for outdoor sports. Therefore, you may want to use "med" or "high" for outdoor sports to better reflect typical conditions.

#### Returns:
- `int`: Risk value (0-3).

#### Example:
```python
from main import calculate_risk_value

risk = calculate_risk_value(
    lat=-33.8688,
    lon=151.2093,
    tz="Australia/Sydney",
    time_stamp="2024-02-01 15:00:00",
    tdb=30.0,
    rh=60.0,
    sport_id="soccer",
    wind="low"
)
print(f"Heat-stress risk: {risk}")
```

```python
from main import check_calculate_risk_value_grid

for wind in ["low", "med", "high"]:
    check_calculate_risk_value_grid(
        lat=-33.8688,
        lon=151.2093,
        tz="Australia/Sydney",
        time_stamp="2024-02-01 12:00:00",
        sport_id="basketball",
        wind=wind
    )
```

### Running the Script

To run the main script and see performance benchmarks:
```bash
python main.py
```

This will execute the `time_function` which measures the performance of `calculate_risk_value` over multiple runs.
If all the run use different parameters, the caching will not be effective. 
However, if you run the function multiple times with lat and lon close to each other and the same time_stamp while varying only tdb and rh, the caching will significantly speed up the calculations.
We can discuss this further if this is going to be a bottleneck for the data analysis.

## Dependencies

All dependencies are managed via Pipfile.

## Project Structure

- `main.py`: Main script with the `calculate_risk_value` function and utility functions.
- `risk_calculation/`: Module containing MRT calculations and risk equations.
- `figures/`: Directory for generated visualization images.
- `Pipfile` & `Pipfile.lock`: Dependency management files.

## Issues

Sometimes the solver used in the pythermalcomfort library may not converge for certain input conditions, potentially causing errors, I am looking into ways to handle this more gracefully and solve this problem. In the meantime, I think we can go ahead with the code implementation on your end and see how it performs with the actual data and how the new results compare with the previous analysis.