from dataclasses import dataclass
import json
from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    base_path = Path(sys.executable).parent
else:
    base_path = Path(__name__).parent
    
config_path = base_path / "config.json"
config_dict = json.loads(config_path.read_text(encoding="utf-8"))

@dataclass(frozen=True)
class Config:
    HOST: str = config_dict.get("host") # "127.0.0.1"
    PORT: int = config_dict.get("port") # 8585
    CALIB_WL_I: tuple[int] = tuple(config_dict.get("calib_wl_i")) # [4,5]
    