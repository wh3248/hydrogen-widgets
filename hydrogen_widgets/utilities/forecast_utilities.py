"""
    forecast_utilities.py

    Methods to support forecast visualzations.
"""
import os
from datetime import datetime


def get_latest_forecast_file(forecast_nc_path:str)->str:
    """Find the most recent forcast file using the date in the file."""

    found_date = None
    result = None
    for f in os.listdir(forecast_nc_path):
        if f.startswith("forecast.") and f.endswith(".nc"):
            start_pos = len("forecast.")
            end_pos = start_pos + len("MMDDYYYY")
            date_part = f[start_pos:end_pos]
            if found_date is None or datetime.strptime(
                date_part, "%m%d%Y"
            ) > datetime.strptime(found_date, "%m%d%Y"):
                found_date = date_part
                result = f
    return result


def get_forecast_nc_file(domain_path:str, scenario_id:str)->str:
    """Get the forecast nc file from the domain path."""

    forecast_scenario_path = f"{domain_path}/forecast/{scenario_id}"
    if not os.path.exists(forecast_scenario_path):
        raise Exception(
            f"Forecase result directory '{forecast_scenario_path}' does not exist."
        )
    forecast_nc_name = get_latest_forecast_file(forecast_scenario_path)
    forecast_nc_path = f"{forecast_scenario_path}/{forecast_nc_name}"
    if not forecast_nc_path:
        raise Exception("No forecast result file found")
    return forecast_nc_path
