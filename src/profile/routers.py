from fastapi import APIRouter, Depends

router = APIRouter(prefix='/profile', tags=['profile'])


@router.get('/all')
async def get_profiles(service: ProfileService = Depends()):
    profiles = await service.get_profiles()
    return {'status': 200, 'data': {'profiles': profiles}}