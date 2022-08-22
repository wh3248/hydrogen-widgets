"""
    streamflow_points.py
"""
import os
import datetime
from typing import List
import pandas as pd
import plotly.graph_objects as go
import xarray as xr
import dateutil.relativedelta
from hydrogen_common import get_domain_path
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file

# pylint: disable=C0103,R0914,C0200


def render_streamflow_points(user_id:str, domain_id:str)->dict:
    """
    Return the data to render the data for the stremflow points widget.
    This graph responds to global state passed as query parameters to display the points for a selected site.
    This displays observation points for various observation sites types such as "streamflow" or "groundwater".

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
        traces = []
        buttons = []
        obs_sites_path = f"{domain_path}/domain_files/obs_sites.csv"
        OBS = pd.read_csv(obs_sites_path)
        nRows = OBS.shape[0]
        filepath = f"{domain_path}/observations/streamflow/"

        range_min = (
            datetime.datetime.now()
            + dateutil.relativedelta.relativedelta(months=-12 * 2)
        ).strftime("%Y-%m-%d")
        nRows = nRows if nRows <= 8 else 8
        for i in range(nRows):
            if OBS["site_type"][i] == "streamflow":
                streamflow_filepath = filepath + OBS["netcdf_file"][i]
                streamflow = xr.open_dataset(streamflow_filepath)
                streamflow = streamflow.sel(datetime=streamflow.datetime >= range_min)
                nPoints = streamflow["streamflow"].shape[0]
                if nPoints > 0:
                    data = go.Scatter(
                        x=streamflow["datetime"],
                        y=streamflow["streamflow"].round(2),
                        name=OBS["site_name"][i],
                        visible=True,
                    )
                    dates = data["x"].tolist()
                    name = data["name"]
                    entry = {
                        "type": "scatter",
                        "name": name,
                        "x": dates,
                        "y": data["y"].tolist(),
                    }
                    traces.append(entry)
                    button = {"label": name, "method": "update"}
                    buttons.append(button)

        layout = create_layout(buttons)
        response = {"traces": traces, "layout": layout}
        return response
    except Exception as e:
        raise Exception(
            f"Unable to render data for terrain observation points because {str(e)}"
        ) from e


def create_layout(buttons:List[dict])->dict:
    """Create the plotly layout configuration for the graph."""

    for index, button in enumerate(buttons):
        args = [False for j in range(len(buttons))]
        args[index] = True
        button["args"] = [{"visible": args}]

    updatemenus = [
        {
            "buttons": buttons,
            "direction": "down",
            "pad": {"r": 10, "t": 10},
            "showactive": True,
            "x": 0,
            "xanchor": "left",
            "y": 1.2,
            "yanchor": "top",
        }
    ]

    layout = {
        "margin": {"r": 30, "t": 30, "b": 50, "l": 50},
        "updatemenus": updatemenus,
        "yaxis": {
            "title": "Streamflow [CMS]/WTD[m]",
            "autorange": True,
        },
        "xaxis": {
            "title": "Time",
            "type": "date",
            "showgrid": False,
            "showline": True,
            "linewidth": 2,
            "linecolor": "black",
            "rangeslider": {},
            "color": "#198BCA",
        },
    }
    return layout


if __name__ == "__main__":
    # Generate local HTML file for local testing

    # Set env variable to root of simulated user domain root directory
    os.environ["CLIENT_HYDRO_DATA_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tests/test_data")
    )
    # Generate widget result for a user domain in the simulated root directory
    api_result = render_streamflow_points("test_user", "test_domain")

    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
