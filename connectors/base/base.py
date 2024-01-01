from abc import ABC, abstractmethod


class BaseConnector(ABC):
    def __init__(self, host, port, username, password, *args, **kwargs):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, *exc_info):
        self.close_connection()

    @abstractmethod
    def open_connection(self):
        raise NotImplementedError

    @abstractmethod
    def close_connection(self):
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, filename: str):
        raise NotImplementedError
    
    @abstractmethod
    def delete_files_by_extension(self, extension: str, dirname: str = ""):
        raise NotImplementedError

    @abstractmethod
    def get_all_files(self, dirname: str):
        raise NotImplementedError

    @abstractmethod
    def get_file(self, filename: str):
        raise NotImplementedError

    @abstractmethod
    def upload_file(self, *args, **kwargs):
        raise NotImplementedError
