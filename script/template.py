import re
from pathlib import Path

from auto_unpack import __version__ as version
from auto_unpack.util import file

template_dir: Path = Path('auto_unpack/template')
package_version_pattern = re.compile(r'auto-unpack[>=]\=\d+\.\d+\.\d+')


def main():
    """
    更新模板中的版本号
    """
    template_pyproject_toml_files = template_dir.glob('*/pyproject.toml')

    for pyproject_toml_file in template_pyproject_toml_files:
        pyproject_toml = file.read_file(pyproject_toml_file)

        pyproject_toml = re.sub(
            package_version_pattern,
            f'auto-unpack>={version}',
            pyproject_toml
        )

        file.write_file(pyproject_toml_file, pyproject_toml)


if __name__ == '__main__':
    main()
