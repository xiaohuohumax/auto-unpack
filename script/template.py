import re

from auto_unpack import __version__ as version
from auto_unpack.util import file

from .release import template_root_dir

package_version_pattern = re.compile(r"auto-unpack[>=~]\=\d+\.\d+\.\d+")


def main():
    """
    更新模板中的版本号
    """
    print(f"Update template version to {version}.")
    template_pyproject_toml_files = template_root_dir.glob("*/pyproject.toml")

    for pyproject_toml_file in template_pyproject_toml_files:
        pyproject_toml = file.read_file(pyproject_toml_file)

        # MAJOR_TODO: 更新版本号，由于项目处于开发阶段，接口变化较大，
        # 因此使用 ~= 而不是 >=，后期稳定版本发布时再修改为 >=。
        pyproject_toml = re.sub(
            package_version_pattern, f"auto-unpack~={version}", pyproject_toml
        )

        file.write_file(pyproject_toml_file, pyproject_toml)
        print(f"Update {pyproject_toml_file} success.")

    print("Update template version finish.")


if __name__ == "__main__":
    """
    此脚本用于更新模板中的版本号
    """
    main()
