"""
    current_conditions_heatmap.py
"""
import os
from typing import List
from datetime import datetime
from netCDF4 import Dataset
from hydrogen_common import get_domain_path
import plotly.graph_objs as go
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file


def render_current_conditions_heatmap(user_id: str, domain_id: str) -> dict:
    """
    Return API response to support the current conditions heatmap widget.

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
        cc_date = find_recent_current_conditions_date(domain_path)

        # load data for heatmap for the date given above
        file = f"{domain_path}/current_conditions/current_conditions.{cc_date}.nc"
        dataset = Dataset(file)

        # Compute aspect ratio
        aspect_ratio = (
            dataset.variables["soil_moisture"].shape[0]
            / dataset.variables["soil_moisture"].shape[1]
        )

        # Collect data for traces
        traces = []
        traces.append(
            {
                "z": get_z_values(dataset, "soil_moisture"),
                "type": "heatmap",
                "visible": False,
                "colorscale": "Viridis",
                "reversescale": True,
                "colorbar": {"title": "SM [-]"},
            }
        )
        traces.append(
            {
                "z": get_z_values(dataset, "water_table_depth"),
                "visible": True,
                "type": "heatmap",
                "colorscale": "Blues",
                "colorbar": {"title": "WTD [m]"},
            }
        )

        # Create menu buttons
        updatemenus = [
            {
                "buttons": [
                    {
                        "args": [{"visible": [False, True]}],
                        "label": "WTD",
                        "method": "restyle",
                    },
                    {
                        "args": [{"visible": [True, False]}],
                        "label": "SM",
                        "method": "restyle",
                    },
                ],
                "direction": "down",
                "pad": {"r": 10, "t": 10},
                "showactive": True,
                "x": 0.1,
                "xanchor": "left",
                "y": 1.0,
                "yanchor": "top",
            }
        ]

        # Create layout
        layout = {
            "margin": {"r": 0, "t": 30, "b": 50, "l": 50},
            "updatemenus": updatemenus,
            "xaxis": {"title": "X [km]"},
            "yaxis": {"title": "Y [km]"},
        }

        # Return response
        response = {"traces": traces, "layout": layout, "aspectRatio": aspect_ratio}
        return response
    except Exception as e:
        raise Exception("Unable to render current_conditions_heatmap") from e


def get_z_values(dataset: Dataset, value: str) -> List[List[float]]:
    """Generate z values of the plotly heatmap"""

    heatmap = go.Heatmap(z=dataset.variables[value])
    return heatmap["z"].tolist()


def find_recent_current_conditions_date(domain_path: str) -> List[str]:
    """Look in domain_path to find the date of the most recent current_conditions files."""

    result = None
    current_conditions_path = f"{domain_path}/current_conditions"
    for f in os.listdir(current_conditions_path):
        if f.startswith("current_conditions.") and f.endswith(".nc"):
            start_pos = len("current_conditions.")
            end_pos = start_pos + len("MMDDYYYY")
            date_part = f[start_pos:end_pos]
            if result is None or datetime.strptime(
                date_part, "%m%d%Y"
            ) > datetime.strptime(result, "%m%d%Y"):
                result = date_part
    return result


if __name__ == "__main__":
    # Generate local HTML file for local testing

    # Set env variable to root of simulated user domain root directory
    os.environ["CLIENT_HYDRO_DATA_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tests/test_data")
    )
    # Generate widget result for a user domain in the simulated root directory
    api_result = render_current_conditions_heatmap("test_user", "test_domain")

    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
