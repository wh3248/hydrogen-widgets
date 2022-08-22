import os
import json

def create_plotly_html_file(basefile_name:str, api_result:dict):
    """
    Create an .html in the directory with the widget source code
    to visualize a widget locally for testing and development
    purposes. 


    Parameters
    ----------
    basefile_name : str
        Value of the __file__ from the main file of the widget implementation.
        This is used to get the absolute path name to the main file directory and the name of the widget.
    api_result: dict
        Value of the dictionary result returned after running the widget method.
        this value is substituted into a html template to simulate rendering of the widget
        by the UI in javascript in the real application.
    Returns
    -------
        None
    """        

    target_path = os.path.abspath(os.path.dirname(basefile_name))
    target_name = os.path.basename(basefile_name).replace(".py", "")
    from_path = os.path.dirname(__file__)
    with open(f"{from_path}/data/demo.html", "r") as stream:
        contents = stream.read()
        contents = contents.replace("${API_RESULT}", json.dumps(api_result, indent=2))
    html_file = f"{target_path}/{target_name}.html"
    with open(html_file, "w+") as stream:
        stream.write(contents)
    try:
        os.system(f"open {html_file}")
    except:
        pass
