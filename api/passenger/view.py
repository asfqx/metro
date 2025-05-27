from fastapi import APIRouter, Depends, HTTPException, status
from .schema import CreateLine
from .crud import create_line


router = APIRouter(tags=["line"], prefix='line')


@router.post('/', response_model=CreateLine, status_code=status.HTTP_201_CREATED)
def route_create_line(line: CreateLine, session: AsyncSession = Depends(get_db)):
    return create_line(session, line)

