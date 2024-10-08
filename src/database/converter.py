from src.common.objects import Metadata, VaultType, FileType
from src.database.models import TrackedFolder


def cvt_tracked_folder_to_metadata(tracked_folder: TrackedFolder) -> Metadata:
    return Metadata(
        name=tracked_folder.name,
        vault_id=tracked_folder.vault_id,
        vault_type=VaultType(tracked_folder.vault_type.value),
        file_type=FileType.FOLDER,
        link=tracked_folder.path,
        create_date=tracked_folder.create_date,
        update_date=tracked_folder.update_date,
    )