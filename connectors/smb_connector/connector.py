import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from typing import IO

from smb.SMBConnection import SMBConnection

from connectors.base import BaseConnector
from connectors.smb_connector.schemas import SMBFile


class SMBConnector(BaseConnector):
    def __init__(
            self,
            remote_name: str = "SHARE2",
            my_name: str = "guest",
            shared_folder: str | None = None,
            work_dir: str | None = None,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.remote_name = remote_name
        self.my_name = my_name
        self.conn = SMBConnection(
            username=self._username,
            password=self._password,
            my_name=self.my_name,
            remote_name=self.remote_name,
            is_direct_tcp=True,
        )
        self._shared_folder = shared_folder
        self._work_dir = work_dir

    def delete_file(self, file_pattern: str, delete_folders: bool = False) -> None:
        full_pattern = "/".join([self._work_dir, file_pattern])
        self.conn.deleteFiles(self._shared_folder, full_pattern, delete_folders)

    def delete_files_by_extension(self, extension: str, dirname: str = "", delete_folders: bool = False) -> None:
        full_pattern = "/".join([self._work_dir, f"*.{extension}"])
        self.conn.deleteFiles(self._shared_folder, full_pattern, delete_folders)

    def create_connection(self):
        assert self.conn.connect(ip=self._host, port=self._port,)

    def close_connection(self):
        self.conn.close()

    def get_all_files(self, dirname: str = "") -> list[SMBFile]:
        full_path = "/".join([self._work_dir, dirname])
        _files_list = self.conn.listPath(self._shared_folder, full_path)
        files_list = [
            SMBFile(
                is_dir=f.isDirectory,
                name=f.filename,
                read_only=f.isReadOnly,
            )
            for f in _files_list
        ]
        for file in files_list[:]:
            if file.is_dir and file.name in (".", ".."):
                files_list.remove(file)
        return files_list

    @contextmanager
    def get_file(self, path: str) -> Iterator[IO[bytes]]:
        full_path = "/".join([self._work_dir, path])
        file_obj = tempfile.NamedTemporaryFile()
        try:
            _, _ = self.conn.retrieveFile(self._shared_folder, full_path, file_obj)
            file_obj.seek(0)
            yield file_obj.file
        finally:
            file_obj.close()

    def upload_file(self, path: str, file_obj: IO) -> bool:
        full_path = "/".join([self._work_dir, path])
        bytes_count = self.conn.storeFile(self._shared_folder, full_path, file_obj)
        if bytes_count:
            return True
        return False

    def delete_files(self, file_pattern: str, delete_folders: bool = False) -> None:
        full_pattern = "/".join([self._work_dir, file_pattern])
        self.conn.deleteFiles(self._shared_folder, full_pattern, delete_folders)

    def create_dir(self, path: str) -> None:
        full_path = "/".join([self._work_dir, path])
        dirs = full_path.split("/")
        current_path = ""
        while dirs:
            current_path += f"{dirs.pop(0)}/"
            try:
                self.conn.createDirectory(self._shared_folder, current_path)
            except OperationFailure:
                pass

    def delete_dir(self, path: str) -> None:
        full_path = "/".join([self._work_dir, path])
        self.conn.deleteDirectory(self._shared_folder, full_path)

    def copy_file(self, old_path: str, new_path: str) -> None:
        full_old_path = "/".join([self._work_dir, old_path])
        full_new_path = "/".join([self._work_dir, new_path])
        with tempfile.NamedTemporaryFile() as file_obj:
            self.conn.retrieveFile(self._shared_folder, full_old_path, file_obj)
            file_obj.seek(0)
            self.conn.storeFile(self._shared_folder, full_new_path, file_obj)

    def move_file(self, old_path: str, new_path: str) -> None:
        self.copy_file(old_path=old_path, new_path=new_path)
        full_old_path = "/".join([self._work_dir, old_path])
        self.conn.deleteFiles(self._shared_folder, full_old_path)
