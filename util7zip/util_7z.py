import subprocess
from pathlib import Path


def choose(flag, true_cho, false_cho):
    return true_cho if flag else false_cho


class Util7z(object):
    lib7zip_path: str = str(Path(Path(__file__).parent, 'lib7zip/7z.exe'))

    @classmethod
    def unpack(cls, file_path: str, password: str = "", unpack_path: str = "", over_write_model: str = 't',
               keep_dir: bool = True) -> (int, str):
        # cmd: 7z.exe x/e file -y -sdel? -ao[a/s/t/u] -oouput_path -ppassword
        cmd_list = [
            cls.lib7zip_path,
            choose(keep_dir, 'x', 'e'),
            f'"{file_path}"',
            '-y',
            f'-ao{over_write_model}',
            choose(unpack_path, f'-o"{unpack_path}"', ''),
            f'-p"{password}"'
        ]
        return subprocess.getstatusoutput(' '.join(cmd_list))

    @classmethod
    def test(cls, file_path: str, password: str = '') -> (int, str):
        # cmd: 7z.exe t file -ppassword -y
        cmd_list = [
            cls.lib7zip_path,
            't',
            f'"{file_path}"',
            f'-p"{password}"',
            '-y'
        ]
        return subprocess.getstatusoutput(" ".join(cmd_list))

    @classmethod
    def info(cls):
        pass


if __name__ == '__main__':
    print(Util7z.test(r'D:\Workspace\Python\auto-unpack\pack\pack.7z', '1 2')[1])
