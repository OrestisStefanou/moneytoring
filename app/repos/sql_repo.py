from typing import Any, Iterable, List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

class SQLRepo:
    def __init__(self, session: AsyncSession, model: Any) -> None:
        """
        Parameters
        ----------
        session : AsyncSession
            Async databsae session
        model : SQLModel
            The SQLModel that the sql repo will operate on
        """
        self._session = session
        self._model = model

    async def get(self, _id: Any) -> Any:
        """
        Get a single row by its primary key
        Returns an SQLModel of this row or None if row
        doesn't exist
        """
        result = await self._session.get(self._model, _id)
        return result
    
    async def get_all(self) -> List[Any]:
        """
        Select all rows from the table
        Returns a list of SQLModels
        """
        results = await self._session.exec(select(self._model))
        return results.all()
    
    async def iter_all(self) -> Iterable[Any]:
        """
        Select all rows from the table
        Returns an iterable of SQLModels
        """
        results = await self._session.exec(select(self._model))
        return results