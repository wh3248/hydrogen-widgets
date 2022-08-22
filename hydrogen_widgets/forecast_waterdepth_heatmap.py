"""
    forecast_waterdepth_heatmap.py
"""
import os
from netCDF4 import Dataset
import xarray as xr
import numpy as np
from hydrogen_common import get_domain_path, get_domain_state
import plotly.graph_objs as go
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file
from hydrogen_widgets.utilities.forecast_utilities import (
    get_forecast_nc_file,
)


def render_forecast_waterdepth_heatmap(
    user_id: str, domain_id: str, query_parameters: dict
) -> dict:
    """
    Return API response to support the forecast_waterdepth_heatmap widget.

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

        ds = xr.open_mfdataset(forecast_nc_path)
        var = "water_table_depth"
        wtd0 = ds[var].isel(member=0)
        wtd1 = ds[var].isel(member=1)
        wtd2 = ds[var].isel(member=2)
        wtd3 = ds[var].isel(member=3)

        delta0 = np.nan_to_num(np.array(wtd0)[0] - np.array(wtd0)[-1])
        delta1 = np.nan_to_num(np.array(wtd1)[0] - np.array(wtd1)[-1])
        delta2 = np.nan_to_num(np.array(wtd2)[0] - np.array(wtd2)[-1])
        delta3 = np.nan_to_num(np.array(wtd3)[0] - np.array(wtd3)[-1])

        start = np.array(wtd0)[0]

        traces = []
        traces.append(
            {
                "type": "heatmap",
                "name": "WDT",
                "colorscale": "Blues",
                "colorbar": {"title": "WDT      "},
                "visible": True,
                "z": get_z_values(start),
            }
        )
        traces.append(
            {
                "type": "heatmap",
                "name": "WDT Change",
                "colorscale": "Blues",
                "colorbar": {"title": "WTD Change Run 1"},
                "visible": False,
                "z": get_z_values(delta0),
            }
        )
        traces.append(
            {
                "type": "heatmap",
                "name": "WDT Change",
                "colorscale": "Blues",
                "colorbar": {"title": "WTD Change Run 2"},
                "visible": False,
                "z": get_z_values(delta1),
            }
        )
        traces.append(
            {
                "type": "heatmap",
                "name": "WDT Change",
                "colorscale": "Blues",
                "colorbar": {"title": "WTD Change Run 3"},
                "visible": False,
                "z": get_z_values(delta2),
            }
        )
        traces.append(
            {
                "type": "heatmap",
                "name": "WDT Change",
                "colorscale": "Blues",
                "colorbar": {"title": "WTD Change Run 4"},
                "visible": False,
                "z": get_z_values(delta3),
            }
        )
        layout = get_layout(traces)
        response = {"traces": traces, "aspectRatio": aspectRatio, "layout": layout}
        return response
    except Exception as e:
        raise Exception("Unable to render forecast_waterdepth_heatmap") from e


def get_layout(traces):

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


def get_z_values(nparray):
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
    api_result = render_forecast_waterdepth_heatmap(
        "test_user", "test_domain", test_query_parameters
    )
    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
