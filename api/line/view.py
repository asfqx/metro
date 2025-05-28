from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.db_helper import db_helper
from .crud import get_line, create_line, get_lines
from .schema import CreateLine, Line

router = APIRouter(tags=["Line"], prefix="/line")


@router.get("/{line_id}/")
async def r_get_line(
    line_id: int, session: AsyncSession = Depends(db_helper.session_dependency)
):
    line = await get_line(session=session, line_id=line_id)
    if line:
        return line
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/", response_model=Line)
async def r_create_line(
    line_in: CreateLine,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await create_line(session=session, line_in=line_in)


@router.get("/", response_model=list[Line])
async def r_list_lines(session: AsyncSession = Depends(db_helper.session_dependency)):
    return await get_lines(session=session)
