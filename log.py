from dataclasses import dataclass

# importance:
# 0 - None
# 1 - Low
# 2 - High
# 3 - Error

@dataclass
class log:
    id : int
    importance : int
    type : str
    time : str
    message : str