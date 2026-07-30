from typing import Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class YandexDiskClient:

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk'
        self._client: Optional[httpx.AsyncClient] = None
        self._headers: Optional[dict] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        self._headers = {
            'Authorization': f'OAuth {self.token}'
        } if self.token else {}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _ensure_initialized(self) -> tuple[httpx.AsyncClient, dict]:
        if self._client is None:
            raise RuntimeError(
                'YandexDiskClient не инициализирован.'
                ' Используйте "async with".'
            )
        return self._client, self._headers

    async def create_excel_file(
        self, title: str, folder: str = 'QRKot_Reports'
    ) -> tuple[str, str]:
        client, headers = await self._ensure_initialized()
        await self._create_folder(folder)

        file_path = f'disk:/{folder}/{title}.xlsx'

        response = await client.get(
            f'{self.base_url}/resources/upload',
            headers=headers,
            params={'path': file_path, 'overwrite': 'true'},
        )
        response.raise_for_status()

        upload_url = response.json().get('href')
        if not upload_url:
            raise ValueError('Не удалось получить ссылку для загрузки')

        return upload_url, file_path

    async def upload_file(self, upload_url: str, content: bytes) -> None:
        client, headers = await self._ensure_initialized()
        response = await client.put(
            upload_url,
            content=content,
            headers={
                'Content-Type': (
                    'application/vnd.openxmlformats-officedocument.'
                    'spreadsheetml.sheet'
                )
            },
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        client, headers = await self._ensure_initialized()

        response = await client.put(
            f'{self.base_url}/resources/publish',
            headers=headers,
            params={'path': file_path},
        )
        response.raise_for_status()

        response = await client.get(
            f'{self.base_url}/resources',
            headers=headers,
            params={'path': file_path},
        )
        response.raise_for_status()

        public_url = response.json().get('public_url')
        if not public_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Ссылка не была получена со стороны Яндекс Диска',
            )

        return public_url

    async def _create_folder(self, folder: str) -> None:
        client, headers = await self._ensure_initialized()
        try:
            await client.put(
                f'{self.base_url}/resources',
                headers=headers,
                params={'path': f'disk:/{folder}'},
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 409:
                raise


async def get_yandex_client():
    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Яндекс Диск не настроен.'
            ' Добавьте YANDEX_DISK_TOKEN в .env',
        )

    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client
