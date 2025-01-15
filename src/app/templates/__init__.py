from fastapi.templating import Jinja2Templates

from pathlib import Path

PATH_TEMPLATES = Path(__file__).parent
templates = Jinja2Templates(directory=PATH_TEMPLATES)
# this object is used in the routers to locate the templates in the filesystem
