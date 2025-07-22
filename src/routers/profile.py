from fastapi import APIRouter

router = APIRouter(prefix='/profile', tags=['profile'])


@router.get('/all')
async def get_profiles():
    return {'status': 200}