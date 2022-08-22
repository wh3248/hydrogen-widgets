"""
    scenarioes_timeseries.py
"""

import os
import glob
from typing import List
from hydrogen_common import get_domain_path
import xarray as xr
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file

# pylint: disable=C0103,R0914,C0200


def render_scenario_timeseries(user_id:str, domain_id:str, query_parameters:dict)->dict:
    """
    Return API response to support the scenarioes timeseries widget.

    Parameters
    ----------
    user_id: str
        User id of the domain to get data.
    domain_id: str
        Domain id that identifies the user domain containing the widget data.
    query_parameters: dict
        A dictionary of options sent by query parameters to the API. This must include the
        option 'scenario_id'.

    Returns
    -------
    dict
        A dictionary (json structure) containing the response to be sent back to the UI
    """

    ## interactive scenario plotter widget
    ## R Maxwell / L Condon
    ## reedmaxwell@princeton.edu / lecondon@arizona.edu
    ## demo for hydroGEN 29-May-22

    ## reads all scenario forcing from a user's directory and domain, plots averages by variables
    ## inspired by https://docs.datapane.com/examples-and-tutorials/interactive-filters

    try:
        domain_path = get_domain_path(user_id=user_id, domain_directory=domain_id)
        scenario_id = query_parameters.get("scenario_id", None)
        if not scenario_id:
            raise Exception("No scenario_id specified")

        traces = []

        # Get a list of scenario files
        directory = f"{domain_path}/scenarios/{scenario_id}"
        file_list = glob.glob(directory + "/*run*")

        ## Read in just one ensemble member to the number of timesteps and the variable list
        run1 = xr.open_dataset(file_list[0])
        n_members = len(file_list)
        var_list = list(run1.data_vars)
        ## add human readable names for buttons
        var_name = ["Precip", "Temp_min", "Temp_max", "Temp_mean", "Solar"]
        ## add descriptive axes for each plot
        axis_name = [
            "Precipitation [mm]",
            "Min Daily Temp [K]",
            "Max Daily Temp [K]",
            "Avg Daily Temp [K]",
            "Daily Shortwave Radiation [W/m^2]",
        ]
        ## turn off all plots except precip when first viewed
        vis_init = [True, False, False, False, False]

        # Read the NetCDF files and concatenate all of the ensemble members together
        ens_list = []
        for i in range(n_members):
            ds = xr.open_dataset(file_list[i])
            ens_list.append(ds)

        ens_ds = xr.concat(ens_list, dim="member")
        dates = ens_ds.time.values.squeeze()
        for j in range(len(var_list)):
            for i in range(n_members):
                temp_plot = ens_ds[var_list[j]].mean(dim=["x", "y"]).values.squeeze()
                # get the spatially averaged values for a given variable
                trace_name = f"{var_name[j]}: Run {i+1}"
                trace = dict(
                    type="scatter",
                    line={"width": 2},
                    x=[str(d) for d in dates],
                    y=list(temp_plot[i, :]),
                    name=trace_name,
                    visible=vis_init[j],
                )
                traces.append(trace)

        # Create Plotly layout and return response
        layout = create_layout(var_list, n_members, var_name, axis_name)
        response = {"traces": traces, "layout": layout}
        return response
    except Exception as e:
        raise Exception("Unable to render render_scenario_timeseries") from e


def create_layout(var_list:List[str], n_members:int, var_name:str, axis_name:str)->dict:
    """Create the plotly layout to draw the graph."""

    # assign buttons, the plan is that all the variables and all realizations are plotted in the Figure
    # a button for a given variable sets the lines that correpond to it's realizations "visible" while the
    # visibility for realizations for all other variables is set to "False"
    buttons = []

    for j in range(len(var_list)):
        args = (
            [False] * n_members * len(var_list)
        )  # set a matrix of "visible" arguments that is n_var X n_real
        for i in range(n_members):
            args[
                (j * (n_members) + i)
            ] = True  # set visiblity for all realizations for a given var to "true"

        # create a button for each variable in the scenario list, use HR names and dynamic axes
        button = dict(
            label=f"{var_name[j]}",
            method="update",
            args=[
                {"visible": args},
                {
                    "yaxis": {
                        "title": f"{axis_name[j]}",
                        "showgrid": False,
                        "showline": True,
                        "linewidth": 2,
                        "linecolor": "black",
                        "mirror": True,
                    }
                },
            ],
        )
        # add the button to our list of buttons
        buttons.append(button)

    layout = dict(
        updatemenus=[
            dict(
                active=0,
                type="dropdown",
                buttons=buttons,
                x=0,
                y=1.1,
                xanchor="left",
                yanchor="bottom",
            )
        ],
        autosize=False,
        margin=dict(r=0, t=65, b=0, l=60),
        xaxis=dict(
            title=dict(text="Date"),
            type="date",
            autorange=True,
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor="black",
            rangeslider=dict(visible=True),
            mirror=True,
        ),
        yaxis=dict(
            title=dict(text=axis_name[0]),  # axis is precip when first viewed
            autorange=True,
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
        ),
    )
    return layout


if __name__ == "__main__":
    # Generate local HTML file for local testing

    # Set env variable to root of simulated user domain root directory
    os.environ["CLIENT_HYDRO_DATA_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tests/test_data")
    )
    # Generate widget result for a user domain in the simulated root directory
    test_query_parameters = {"scenario_id": "test_average"}
    api_result = render_scenario_timeseries(
        "test_user", "test_domain", test_query_parameters
    )
    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
