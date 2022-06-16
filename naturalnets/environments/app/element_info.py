import attr

from typing import Tuple, List
from widget import Widget_old

@attr.s(slots=True, auto_attribs=True, kw_only=True)
class ElementInfo:
    name:str
    constraint_names:List[str] = []
    constraint_indexes:List[int] = []
    widget:Widget_old
    widget_name:str
    state_sector:Tuple[int,int]
    page_name:str


