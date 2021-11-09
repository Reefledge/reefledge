import os
from multiprocessing.dummy import Lock
import shutil
from zipfile import ZipFile

from .ftp_client import FTPClientPublic
from .remote_zip_file_path import infer_remote_zip_file_path


def setup() -> None:
    this_dir_name: str = os.path.dirname(__file__)

    with Lock(): # Ensure thread safety.
        if 'reefledge' not in os.listdir(this_dir_name) or _version_mismatch():
            _setup()


def _version_mismatch() -> bool:
    from .version import __version__
    rl_package_wrapper_version: str = __version__

    from .reefledge.version import __version__
    rl_compiled_cython_package_version: str = __version__

    answer = (rl_package_wrapper_version != rl_compiled_cython_package_version)

    if answer:
        __remove_reefledge_compiled_cython_package()

    return answer

def __remove_reefledge_compiled_cython_package() -> None:
    target_directory_name: str = os.path.join(
        os.path.dirname(__file__),
        'reefledge'
    )

    shutil.rmtree(target_directory_name)


def _setup() -> None:
    original_cwd: str = os.getcwd()
    os.chdir(os.path.dirname(__file__))

    try:
        _download_reefledge_compiled_cython_package()
    finally:
        os.chdir(original_cwd)

def _download_reefledge_compiled_cython_package() -> None:
    with FTPClientPublic() as ftp_client:
        remote_zip_file_path = infer_remote_zip_file_path(ftp_client)
        ftp_client.retrieve_file(remote_zip_file_path)

    zip_file_name: str = os.path.basename(remote_zip_file_path)
    __extract_zip_file(zip_file_name)

def __extract_zip_file(zip_file_name: str) -> None:
    with ZipFile(zip_file_name, 'r') as zf:
        zf.extractall(path=os.path.dirname(__file__))

    os.remove(zip_file_name)
