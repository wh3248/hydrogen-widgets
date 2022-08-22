"""
    forecast_soilmoisture_heatmap.py
"""
import os
from typing import List
from netCDF4 import Dataset
import xarray as xr
import numpy as np
from hydrogen_common import get_domain_path, get_domain_state
import plotly.graph_objs as go
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file
from hydrogen_widgets.utilities.forecast_utilities import (
    get_forecast_nc_file
)


def render_forecast_soilmoisture_heatmap(
    user_id: str, domain_id: str, query_parameters: dict
) -> dict:
    """
    Return API response to support the forecast_soilmoisture_heatmap widget.

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
        domain_state = get_domain_state(user_id=user_id, domain_directory=domain_id)
        grid_bounds = domain_state["grid_bounds"]
        scenario_id = query_parameters.get("scenario_id", None)
        aspectRatio = round(
            (grid_bounds[3] - grid_bounds[1]) / (grid_bounds[2] - grid_bounds[0]), 3
        )
        forecast_nc_path = get_forecast_nc_file(domain_path, scenario_id)

        static_domain_variables = (
            f"{domain_path}/domain_files/static_domain_variables.nc"
        )
        ds = xr.open_mfdataset([forecast_nc_path, static_domain_variables])

        wtd0 = np.array(
            np.nan_to_num(np.array(ds["saturation"].isel(member=0)))
            * np.nan_to_num(np.array(ds["porosity"]))
        )[:, -1]
        wtd1 = np.array(
            np.nan_to_num(np.array(ds["saturation"].isel(member=1)))
            * np.nan_to_num(np.array(ds["porosity"]))
        )[:, -1]
        wtd2 = np.array(
            np.nan_to_num(np.array(ds["saturation"].isel(member=2)))
            * np.nan_to_num(np.array(ds["porosity"]))
        )[:, -1]
        wtd3 = np.array(
            np.nan_to_num(np.array(ds["saturation"].isel(member=3)))
            * np.nan_to_num(np.array(ds["porosity"]))
        )[:, -1]

        delta0 = np.array(wtd0)[0] - np.array(wtd0)[-1]
        delta1 = np.array(wtd1)[0] - np.array(wtd1)[-1]
        delta2 = np.array(wtd2)[0] - np.array(wtd2)[-1]
        delta3 = np.array(wtd3)[0] - np.array(wtd3)[-1]

        start = np.array(wtd0)[0]

        traces = []
        traces.append(
            {
                "type": "heatmap",
                "name": "Soil Moisture",
                "colorscale": "Viridis",
                "reversescale": True,
                "colorbar": {"title": "SM      "},
                "visible": True,
                "z": get_z_values(start),
            }
        )
        traces.append(
            {
                "type": "heatmap",
                "name": "SM Change",
                "colorscale": "Viridis",
                "reversescale": True,
                "colorbar": {"title": "SM Change Run 1"},
                "visible": False,
                "z": get_z_values(delta0),
            }
        )
        traces.append(
            {
                "type": "heatmap",
                "name": "SM Change",
                "colorscale": "Viridis",
                "reversescale": True,
                "colorbar": {"title": "SM Change Run 2"},
                "visible": False,
                "z": get_z_values(delta1),
            }
        )
        traces.append(
            {
                "type": "heatmap",
                "name": "SM Change",
                "colorscale": "Viridis",
                "reversescale": True,
                "colorbar": {"title": "SM Change Run 3"},
                "visible": False,
                "z": get_z_values(delta2),
            }
        )
        traces.append(
            {
                "type": "heatmap",
                "name": "SM Change",
                "colorscale": "Viridis",
                "reversescale": True,
                "colorbar": {"title": "SM Change Run 4"},
                "visible": False,
                "z": get_z_values(delta3),
            }
        )
        layout = get_layout(traces)
        response = {"traces": traces, "aspectRatio": aspectRatio, "layout": layout}
        return response
    except Exception as e:
        raise Exception("Unable to render forecast_soilmoisture_heatmap") from e


def get_layout(traces: List[dict]) -> dict:
    """Get the plotly layout configuration for the heatmap."""

    buttons = []
    for i, trace in enumerate(traces):
        args = [False for i in range(0, len(traces))]
        args[i] = True
        button = {
            "label": trace.get("colorbar").get("title"),
            "method": "update",
            "args": [{"visible": args}],
        }
        buttons.append(button)

    updatemenus = [
        {
            "buttons": buttons,
            "direction": "down",
            "pad": {"r": 10, "t": 10},
            "showactive": True,
            "x": 0,
            "xanchor": "left",
            "y": "1.0",
            "yanchor": "top",
        }
    ]

    layout = {
        "margin": {"r": 0, "t": 30, "b": 50, "l": 50},
        "updatemenus": updatemenus,
        "xaxis": {"title": "X [km]"},
        "yaxis": {"title": "Y [km]"},
    }
    return layout


def get_z_values(nparray: np.ndarray) -> List[List[float]]:
    """Generate z values of the plotly heatmap"""

    heatmap = go.Heatmap(z=nparray)
    return heatmap["z"].tolist()


if __name__ == "__main__":
    # Generate local HTML file for local testing

    # Set env variable to root of simulated user domain root directory
    os.environ["CLIENT_HYDRO_DATA_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tests/test_data")
    )
    # Generate widget result for a user domain in the simulated root directory
    test_query_parameters = {"scenario_id": "test_average"}
    api_result = render_forecast_soilmoisture_heatmap(
        "test_user", "test_domain", test_query_parameters
    )
    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
