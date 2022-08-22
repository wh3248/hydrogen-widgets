"""
    Get the api_results for a visualization widget.
    This is called by the hydrogen API when a widget is requested.
"""
from hydrogen_widgets.current_conditions_heatmap import render_current_conditions_heatmap
from hydrogen_widgets.location_map import render_location_map
from hydrogen_widgets.terrain_map import render_terrain_map
from hydrogen_widgets.terrain_obs_points import render_terrain_obs_points
from hydrogen_widgets.forecast_soilmoisture_heatmap import render_forecast_soilmoisture_heatmap
from hydrogen_widgets.forecast_waterdepth_heatmap import render_forecast_waterdepth_heatmap
from hydrogen_widgets.forecast_timeseries import render_forecast_timeseries
from hydrogen_widgets.streamflow_points import render_streamflow_points
from hydrogen_widgets.scenarios_timeseries import render_scenario_timeseries

def get_widget_result(datasource:str, user_id:str, domain_id:str, query_parameters:dict=None)->dict:
    """
    Execute the code to get the requested visualization result for a datasource.

    Parameters
    ----------
    datasource : str
        Name of the datasource passed in from the API request that identifies the widget.
    user_id: str
        User id of the domain to get data.
    domain_id: str
        Domain id that identifies the user domain containing the widget data.
    query_parameters: dict
        A dictionary of optional options passed to the widget using the query parameters
        from the API request. This may be None of there are no options.
    Returns
    -------
    response: dict
        A dictionary (json structure) containing the response to be sent back to the UI
        to render the widget in the UI. Returns None if the datasoruce is not supported.
    """    

    result = None
    if datasource:
        if datasource == "current_conditions_heatmap":
            result = render_current_conditions_heatmap(user_id, domain_id)
        elif datasource == "location_map":
            result = render_location_map(user_id, domain_id)
        elif datasource == "terrain_map":
            result = render_terrain_map(user_id, domain_id)
        elif datasource == "terrain_obs_points":
            result = render_terrain_obs_points(user_id, domain_id, query_parameters)
        elif datasource == "forecast_soilmoisture_heatmap":
            result = render_forecast_soilmoisture_heatmap(user_id, domain_id, query_parameters)
        elif datasource == "forecast_watertable_heatmap":
            result = render_forecast_waterdepth_heatmap(user_id, domain_id, query_parameters)
        elif datasource == "forecast_time_series":
            result = render_forecast_timeseries(user_id, domain_id, query_parameters)
        elif datasource == "observation_points":
            result = render_streamflow_points(user_id, domain_id)
        elif datasource == "scenario_timeseries":
            result = render_scenario_timeseries(user_id, domain_id, query_parameters)
    return result
