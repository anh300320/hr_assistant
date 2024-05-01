import logging
import os
import random
import time
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.common.exceptions import InternalException
from src.vault.base import Vault, Metadata

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
RETRY = 6
PAGE_SIZE = 20


class GoogleDrive(Vault):

    def load_content(self, metadata: Metadata):
        pass

    def __init__(self, config):
        super().__init__(config)
        self._vault_root = config.get('google_drive_folder', None)
        self._google_credential_dir = config.get(
            'google_credential_dir',
            'resources'
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
                fields="nextPageToken, files(id, name, webContentLink)",
                page_token=next_page_token,
            )
            next_page_token = resp.get("nextPageToken")
            for file in resp.get("files", []):
                metadata = Metadata(
                    name=file['name'],
                    internal_id=file['id'],
                    link=file.get('webContentLink'),
                )
                metadatas.append(metadata)
        return metadatas

    def _load_folder_id(
            self,
            folder_name: str
    ) -> str:
        credentials = self._auth()
        resp = self._list_file(
            credentials=credentials,
            page_size=1,
            query=f"mimeType='application/vnd.google-apps.folder' and name = '{folder_name}'"
        )
        folders = resp.get("files", [])
        if len(folders) == 0:
            raise InternalException(
                f"Folder not found {self._vault_root}"
            )
        elif len(folders) > 1:
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
