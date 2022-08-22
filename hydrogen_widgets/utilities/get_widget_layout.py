import os
import json

def get_widget_layout()->dict:
    """
    Get the layout of widgets for all the dashboard and sub-dashboard of the application.
    The layout is found in the folder hydrogen_widgets/utilities/data/dashboard_config.json

    Parameters
    ----------
    None

    Returns
    -------
    widget_configuration: dict
        Dictionary of dashboards to a dict defining the layout of the widgets for that dashboard.
        Each dashboard dict contains attributes:
            column_widths:       Array of columns widths. May be number(n) or percent (n%)
            row_heights:         Array of row widgets. may be a number(n) or percent (n%).
            widgets:             Array of widgets.
        Each widget is a dict containing attributes:
            type:                Type of widget supported by the React application. E.g. "plotly".
            title:               Title of the widget displayed above the widget in application.
            datasource:          Datasource of the wiget. This is passed to API to get the data.
            rowspan:             Optional. Number of rows the widget should span.
            colspan:             Optional. Number of columns the widget should span.
    """    

    result = []
    from_path = os.path.dirname(__file__)
    with open(f"{from_path}/data/dashboard_config.json", "r") as stream:
        contents = stream.read()
        result = json.loads(contents)
    return result
