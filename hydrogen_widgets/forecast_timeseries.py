"""
    forecast_timeseries_heatmap.py
"""
import os
from datetime import datetime
from netCDF4 import Dataset
import xarray as xr
import numpy as np
from hydrogen_common import get_domain_path, get_domain_state
import plotly.graph_objs as go
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file
from hydrogen_widgets.utilities.forecast_utilities import (
    get_forecast_nc_file,
    get_latest_forecast_file,
)


def render_forecast_timeseries(user_id:str, domain_id:str, query_parameters:dict)->dict:
    """
    Return API response to support the forecast_timeseries_heatmap widget.

    Parameters
    ----------
    user_id: str
        User id of the domain to get data.
    domain_id: str
        Domain id that identifies the user domain containing the widget data.

    Returns
    -------
    dict
        A dictionary (json structure) containing the response to be sent back to the UI
    """

    try:
        domain_path = get_domain_path(user_id=user_id, domain_directory=domain_id)
        scenario_id = query_parameters.get("scenario_id", None)
        forecast_nc_path = get_forecast_nc_file(domain_path, scenario_id)
        static_domain_variables = (
            f"{domain_path}/domain_files/static_domain_variables.nc"
        )
        ds = xr.open_mfdataset([forecast_nc_path, static_domain_variables])
        (t, x, y) = ds["water_table_depth"].isel(member=0).shape

        sm0 = np.array(
            np.nan_to_num(np.array(ds["saturation"].isel(member=0)))
            * np.nan_to_num(np.array(ds["porosity"]))
        ).sum(axis=-1).sum(axis=-1)[:, -1] / (x * y)
        sm1 = np.array(
            np.nan_to_num(np.array(ds["saturation"].isel(member=1)))
            * np.nan_to_num(np.array(ds["porosity"]))
        ).sum(axis=-1).sum(axis=-1)[:, -1] / (x * y)
        sm2 = np.array(
            np.nan_to_num(np.array(ds["saturation"].isel(member=2)))
            * np.nan_to_num(np.array(ds["porosity"]))
        ).sum(axis=-1).sum(axis=-1)[:, -1] / (x * y)
        sm3 = np.array(
            np.nan_to_num(np.array(ds["saturation"].isel(member=3)))
            * np.nan_to_num(np.array(ds["porosity"]))
        ).sum(axis=-1).sum(axis=-1)[:, -1] / (x * y)

        wtd0 = np.nan_to_num(np.array(ds["water_table_depth"].isel(member=0)).sum(axis=-1).sum(
            axis=-1
        ) / (x * y))
        wtd1 = np.nan_to_num(np.array(ds["water_table_depth"].isel(member=1)).sum(axis=-1).sum(
            axis=-1
        ) / (x * y))
        wtd2 = np.nan_to_num(np.array(ds["water_table_depth"].isel(member=2)).sum(axis=-1).sum(
            axis=-1
        ) / (x * y))
        wtd3 = np.nan_to_num(np.array(ds["water_table_depth"].isel(member=3)).sum(axis=-1).sum(
            axis=-1
        ) / (x * y))

        # Collect soil moisture values (0-3)
        sm_traces = []
        dates = ds.time.values.squeeze()

        # Add soil moisture line graph traces
        colors = ["blue", "red", "green", "purple"]
        sm_traces.append(
            {
                "name": "Run 1",
                "type": "scatter",
                "line": {"width": 4, "color": colors[0]},
                "x": [str(d) for d in dates],
                "y": go.Scatter(y=(sm0 - sm0[0]))["y"].tolist(),
            }
        )
        sm_traces.append(
            {
                "name": "Run 2",
                "type": "scatter",
                "line": {"width": 4, "color": colors[1]},
                "x": [str(d) for d in dates],
                "y": go.Scatter(y=(sm1 - sm1[0]))["y"].tolist(),
            }
        )
        sm_traces.append(
            {
                "name": "Run 3",
                "type": "scatter",
                "line": {"width": 4, "color": colors[2]},
                "x": [str(d) for d in dates],
                "y": go.Scatter(y=(sm2 - sm2[0]))["y"].tolist(),
            }
        )
        sm_traces.append(
            {
                "name": "Run 4",
                "type": "scatter",
                "line": {"width": 4, "color": colors[3]},
                "x": [str(d) for d in dates],
                "y": go.Scatter(y=(sm3 - sm3[0]))["y"].tolist(),
            }
        )
        sm_layout = get_sm_layout()

        # Collect waterdepth values (0-3)
        wt_traces = []
        # Add soil moisture line graph traces
        wt_traces.append(
            {
                "name": "Run 1",
                "type": "scatter",
                "line": {"width": 4, "color": colors[0]},
                "x": [str(d) for d in dates],
                "y": go.Scatter(y=(wtd0 - wtd0[0]))["y"].tolist(),
            }
        )
        wt_traces.append(
            {
                "name": "Run 2",
                "type": "scatter",
                "line": {"width": 4, "color": colors[1]},
                "x": [str(d) for d in dates],
                "y": go.Scatter(y=(wtd1 - wtd1[0]))["y"].tolist(),
            }
        )
        wt_traces.append(
            {
                "name": "Run 3",
                "type": "scatter",
                "line": {"width": 4, "color": colors[2]},
                "x": [str(d) for d in dates],
                "y": go.Scatter(y=(wtd2 - wtd2[0]))["y"].tolist(),
            }
        )
        wt_traces.append(
            {
                "name": "Run 4",
                "type": "scatter",
                "line": {"width": 4, "color": colors[3]},
                "x": [str(d) for d in dates],
                "y": go.Scatter(y=(wtd3 - wtd3[0]))["y"].tolist(),
            }
        )
        wt_layout = get_wt_layout()

        response = {
            "subplots": [
                {"traces": sm_traces, "layout": sm_layout},
                {"traces": wt_traces, "layout": wt_layout},
            ],
            "columns": 1,
        }
        return response
    except Exception as e:
        raise Exception("Unable to render forecast_timeseries") from e


def get_sm_layout()->dict:
    """Get plotly layout to display soil moisture."""

    layout = {
        "margin": {"r": 0, "t": 65, "b": 50, "l": 70},
        "hovermode": "x",
        "title": {
            "text": "Change In Mean Soil Moisture",
            "font": {"color": "#164a8d", "family": "Roboto"},
        },
        "xaxis": {
            "type":"date",
            "title": "Day",
        },
        "yaxis": {"title": "Water Fraction<br>by Volume"},
    }
    return layout


def get_wt_layout()->dict:
    """Get plotly layout to display water table depth."""
    
    layout = {
        "margin": {"r": 0, "t": 65, "b": 50, "l": 70},
        "hovermode": "x",
        "title": {
            "text": "Change In Mean Water Table Depth",
            "font": {"color": "#164a8d", "family": "Roboto"},
        },
        "xaxis": {
            "title": "Day",
            "type":"date"
        },
        "yaxis": {"title": "Height (m)"},
    }
    return layout


if __name__ == "__main__":
    # Generate local HTML file for local testing

    # Set env variable to root of simulated user domain root directory
    os.environ["CLIENT_HYDRO_DATA_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tests/test_data")
    )
    # Generate widget result for a user domain in the simulated root directory
    test_query_parameters = {"scenario_id": "test_average"}
    api_result = render_forecast_timeseries(
        "test_user", "test_domain", test_query_parameters
    )
    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
