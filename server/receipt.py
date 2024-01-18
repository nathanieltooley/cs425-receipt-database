import dataclasses as dc
import datetime as dt


@dc.dataclass
class Receipt:
    key: str
    body: bytes
    upload_dt: dt.datetime = dc.field(
        default_factory=lambda: dt.datetime.now().astimezone()
    )
