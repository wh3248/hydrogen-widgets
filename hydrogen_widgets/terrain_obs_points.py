"""
    terrain_obs_points.py
"""
import os
import datetime
from typing import List
import pandas
import xarray
from hydrogen_common import get_domain_path
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file

# pylint: disable=C0103,R0914,C0200

def render_terrain_obs_points(user_id:str, domain_id:str, query_parameters:dict)->dict:
    """
    Return the data to render the data for the terrain observation points widget.
    This graph responds to global state passed as query parameters to display the points for a selected site.
    This displays observation points for various observation sites types such as "streamflow" or "groundwater".

    Parameters
    ----------
    user_id: str
        User id of the domain to get data.
    domain_id: str
        Domain id that identifies the user domain containing the widget data.
    query_parametes: dict
        A dict containing attributes: site_id, site_name, site_type.
    Returns
    -------
    dict
        A dictionary (json structure) containing the response to be sent back to the UI
    """

    try:
        domain_path = get_domain_path(user_id=user_id, domain_directory=domain_id)
        traces = []
        query_parameters = query_parameters if query_parameters else {}
        site_id = query_parameters.get("site_id", None)
        site_type = query_parameters.get("site_type", None)
        site_name = query_parameters.get("site_name", None)
        if site_type == "streamflow":
            add_obs_points_trace(
                traces, domain_path, site_id, "streamflow", "streamflow"
            )
        if site_type == "groundwater":
            add_obs_points_trace(traces, domain_path, site_id, "groundwater", "wtd")
        layout = create_layout(site_type, site_id, site_name)
        response = {"traces": traces, "layout": layout}
        return response
    except Exception as e:
        raise Exception(
            f"Unable to render data for terrain observation points because {str(e)}"
        ) from e


def create_layout(site_type:str, site_id:str, site_name:str)->dict:
    """Create the plotly layout configuration for the graph."""

    chart_title = site_name
    chart_color = "#198BCA"
    chart_title_size = 14
    if site_type == "streamflow":
        y_axis_title = "Stream Flow (cubic m/s)"
    elif site_type == "groundwater":
        y_axis_title = "Water Depth (m)"
    else:
        y_axis_title = ""

    layout = {
        "title": {
            "text": chart_title,
            "font": {"color": chart_color, "size": chart_title_size},
        },
        "margin": {"r": 30, "t": 80, "b": 40, "l": 50},
        "showlegend": False,
        "zoom": "auto",
        "site_id": site_id,
        "xaxis": {
            "title": "Time",
            "type": "date",
            "rangeslider": {},
            "rangeselector": {
                "buttons": [
                    {"step": "all", "label": "all"},
                    {
                        "count": 12,
                        "label": "1 year",
                        "step": "month",
                        "active": True,
                        "stepmode": "backward",
                    },
                    {
                        "count": 6,
                        "label": "6 months",
                        "step": "month",
                        "active": True,
                        "stepmode": "backward",
                    },
                    {
                        "count": 3,
                        "label": "3 months",
                        "step": "month",
                        "active": True,
                        "stepmode": "backward",
                    },
                ]
            },
            "color": chart_color,
        },
        "yaxis": {
            "title": y_axis_title,
            "autorange": True,
            "rangemode": "tozero",
            "color": chart_color,
        },
    }
    return layout


def add_obs_points_trace(traces:List[dict], domain_path:str, site_id:str, site_type:str, variable_name:List[str]):
    """Get the stream flow data for the stream flow from the domain observations"""

    dir_path = f"{domain_path}/observations/{site_type}/"
    filepath = dir_path + site_id + ".nc"
    ds = xarray.open_dataset(filepath)
    ds = ds.dropna(dim="datetime")
    ds["datetime"] = pandas.DatetimeIndex(ds["datetime"].values)

    # limit the number of months of data returned, but return enough ...
    range_max = datetime.datetime.today().date()
    range_min = range_max - pandas.DateOffset(months=12 * 15)

    # select data from original ds with dates in that range (through present)
    past_six_months = ds.sel(datetime=ds.datetime >= range_min)

    dates = past_six_months["datetime"]
    ds = past_six_months[variable_name]

    dates = dates.to_numpy().tolist()
    values = ds.to_numpy().tolist()

    for date in range(len(dates)):
        dates[date] = datetime.date.fromtimestamp(int(dates[date] / 1000000000))
        dates[date] = dates[date].strftime("%Y-%m-%d")

    traces.append({"mode": "lines", "x": dates, "y": values})


if __name__ == "__main__":
    # Generate local HTML file for local testing

    # Set env variable to root of simulated user domain root directory
    os.environ["CLIENT_HYDRO_DATA_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tests/test_data")
    )
    # Generate widget result for a user domain in the simulated root directory
    test_query_parameters = {
        "site_id": "06713500",
        "site_name": "A test stream gauge",
        "site_type": "streamflow",
    }
    api_result = render_terrain_obs_points(
        "test_user", "test_domain", test_query_parameters
    )

    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
