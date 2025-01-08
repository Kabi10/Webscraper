from dataclasses import dataclass
from typing import Optional

@dataclass
class GoogleAPIConfig:
    api_key: str
    requests_per_second: int = 10
    max_reviews: Optional[int] = None
    min_rating: Optional[float] = None 