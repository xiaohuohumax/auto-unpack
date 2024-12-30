import urllib.request
from pathlib import Path


def download_url(url: str, save_file: Path):
    """
    下载网络资源到本地

    :param url: 网络资源地址
    :param save_file: 本地保存路径
    """
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)
    save_file.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, save_file)
