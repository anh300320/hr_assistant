import io
import logging
import os
import random
import time
from datetime import datetime
from typing import Optional, Union

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from src.common.exceptions import InternalException
from src.common.objects import LoadedFile, LoadedFileType, VaultType, FileType
from src.vault.base import Vault, Metadata

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
RETRY = 6
PAGE_SIZE = 20


class GoogleDrive(Vault):

    vault_type = VaultType.GOOGLE_DRIVE

    def __init__(self, config):
        super().__init__(config)
        self._vault_root = config.get('google_drive_folder', None)
        self._temp_dir = config.get('temp_dir', 'google_drive_temp')
        self._google_credential_dir = config.get(
            'google_credential_dir',
            'resources'
        )

    def _download_file(self, metadata: Metadata) -> LoadedFile:
        os.makedirs(self._temp_dir, exist_ok=True)
        temp_fp = os.path.join(self._temp_dir, metadata.name)
        file_content = self._download_file(metadata)
        with open(temp_fp, 'wb') as fd:
            fd.write(file_content)
        return LoadedFile(
            loaded_type=LoadedFileType.ON_DISK,
            content=temp_fp
        )

    def load_all_metadata(self) -> list[Metadata]:
        folder_id = self._load_folder_id(self._vault_root)
        logging.getLogger(__name__).info(
            "Getting files in folder %s", self._vault_root
        )
        list_files = self._load_all_files_in_folder_recursive(folder_id)
        return list_files

    def _load_all_files_in_folder_recursive(
            self,
            folder_id: str,
    ) -> list[Metadata]:
        children = self._load_children(folder_id)
        files = []
        folders = []
        for metadata in children:
            if not metadata.link:
                folders.append(metadata)
            else:
                files.append(metadata)
        for folder in folders:
            logging.getLogger(__name__).info(
                "Getting children of folder %s",
                folder.name
            )
            nested_files = self._load_all_files_in_folder_recursive(
                folder.vault_id
            )
            files.extend(nested_files)
        return files

    def _load_children(
            self,
            folder_id: str,
    ) -> list[Metadata]:
        credentials = self._auth()
        first_try = True
        next_page_token = None
        metadatas = []
        while first_try or next_page_token:
            first_try = False
            resp = self._list_file(
                credentials=credentials,
                page_size=PAGE_SIZE,
                query=f"'{folder_id}' in parents",
                fields="nextPageToken, files(id, name, webContentLink, mimeType, fullFileExtension, createdTime, modifiedTime)",
                page_token=next_page_token,
            )
            next_page_token = resp.get("nextPageToken")
            for file in resp.get("files", []):
                file_type = self._parse_extension(
                    extension=file.get('fullFileExtension'),
                    mime_type=file.get('mimeType')
                )
                metadata = Metadata(
                    name=file['name'],
                    vault_id=file['id'],
                    vault_type=self.vault_type,
                    link=file.get('webContentLink'),
                    file_type=file_type,
                    create_date=self._parse_date(file.get('createdTime')),
                    update_date=self._parse_date(file.get('modifiedTime'))
                )
                metadatas.append(metadata)
        return metadatas

    def _parse_date(self, dt_str: str) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(dt_str)
        except Exception:
            return None

    def _parse_extension(
            self,
            extension: Optional[str] = None,
            mime_type: Optional[str] = None
    ) -> Union[None, FileType]:
        if extension:
            if extension in ['doc', 'docx']:
                return FileType.DOC
            if extension == 'pdf':
                return FileType.PDF
        if mime_type == 'application/msword':
            return FileType.DOC
        if mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return FileType.DOC
        if mime_type == 'application/pdf':
            return FileType.PDF
        return None

    def _load_folder_id(
            self,
            folder_name: str
    ) -> str:
        credentials = self._auth()
        resp = self._list_file(
            credentials=credentials,
            page_size=20,
            query=f"mimeType='application/vnd.google-apps.folder' and name = '{folder_name}'"
        )
        folders = resp.get("files", [])
        if len(folders) == 0:
            raise InternalException(
                f"Folder not found {self._vault_root}"
            )
        elif len(folders) > 1:
            for folder in folders:
                if folder["name"] == folder_name:
                    return folder['id']
            raise InternalException(
                f"Unexpected number of folder found {folders}",
            )
        return folders[0]['id']

    def _list_file(
            self,
            credentials: Credentials,
            page_size: int = 10,
            fields: str = "nextPageToken, files(id, name)",
            query: Optional[str] = None,
            page_token: Optional[str] = None,
    ):
        for i in range(RETRY):
            try:
                service = build("drive", "v3", credentials=credentials)
                results = (
                    service.files()
                    .list(
                        q=query,
                        pageSize=page_size,
                        fields=fields,
                        pageToken=page_token,
                    )
                    .execute()
                )
                return results
            except HttpError as error:
                logging.getLogger(__name__).exception(
                    "Failed to query files, retrying..."
                )
                time.sleep(2 ** i + random.uniform(0.1, 1.5))
                continue
        raise InternalException(
            f"Failed to query files {query}"
        )

    def _auth(self) -> Credentials:
        """Shows basic usage of the Drive v3 API.
          Prints the names and ids of the first 10 files the user has access to.
          """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_fp = os.path.join(
            self._google_credential_dir,
            'token.json'
        )
        credentials_fp = os.path.join(
            self._google_credential_dir,
            'credentials.json',
        )
        if os.path.exists(token_fp):
            creds = Credentials.from_authorized_user_file(token_fp, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_fp, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_fp, "w") as token:
                token.write(creds.to_json())
        return creds

    def _download_file(
            self,
            metadata: Metadata,
    ) -> bytes:
        creds = self._auth()
        try:
            service = build("drive", "v3", credentials=creds)

            file_id = metadata.vault_id

            # pylint: disable=maybe-no-member
            request = service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            return file.getvalue()
        except HttpError:
            logging.getLogger(__name__).exception(
                "Error occurred when downloading file %s",
                metadata.name
            )
