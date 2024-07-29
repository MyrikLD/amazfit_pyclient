from datetime import datetime

from ..data_fetch import DataFetch, FetchType


class FetchLogs(DataFetch):
    async def start(self, since: datetime):
        await super().start(FetchType.DEBUG_LOGS, since)
