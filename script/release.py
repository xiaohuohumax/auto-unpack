import re
import shutil
from pathlib import Path

from auto_unpack.cli import TemplateAsset, ReleaseAsset, cli_parent_dir, release_json_name
from auto_unpack.util import file

release_root_dir = Path('release')
release_dist_dir = release_root_dir / 'dist'
template_root_dir = release_root_dir / 'template'
template_pkg_json_file = cli_parent_dir / release_json_name
template_release_json_file = release_dist_dir / release_json_name
template_asset_prefix = 'template'


def load_template_description(template_dir: Path) -> str:
    """
    获取模板的描述信息

    :param template_dir: 模板目录
    :return: 模板的描述信息
    """
    pyproject_toml_file = template_dir / 'pyproject.toml'
    description_re = r'description\s*=\s*"(.*)"'
    if not pyproject_toml_file.exists():
        return ''

    pyproject_toml = file.read_file(pyproject_toml_file)
    description = re.findall(description_re, pyproject_toml)
    if not description:
        return ''

    return description[0]


def build_template_release_asset(template_dir: Path) -> Path:
    """
    构建模板的发布资源

    :param template_dir: 模板目录
    :return: 模板的发布资源文件路径
    """
    template_asset_name = f'{template_asset_prefix}-{template_dir.name}'.replace(
        '-', '_')
    archive_file_str = shutil.make_archive(
        base_name=str(release_dist_dir / template_asset_name),
        format='gztar',
        root_dir=str(template_dir)
    )
    return Path(archive_file_str)


def build_template_release():
    """
    构建模板的发布资源
    """
    print('Start building template release assets.')
    release_assets: ReleaseAsset = ReleaseAsset()

    for template_dir in template_root_dir.iterdir():
        description = load_template_description(template_dir)
        print(f'Building release asset for template `{template_dir.name}`.')
        asset_file = build_template_release_asset(template_dir)
        print(
            f'Saving release asset for template `{template_dir.name}` to {asset_file}.')
        release_assets.templates.append(
            TemplateAsset(
                name=template_dir.name,
                description=description,
                asset_name=asset_file.name
            )
        )

    template_json = release_assets.model_dump_json(indent=4)
    print(f'Writing template package json file to {template_pkg_json_file}.')
    file.write_file(template_pkg_json_file, template_json)
    print(
        f'Writing template release json file to {template_release_json_file}.')
    file.write_file(template_release_json_file, template_json)
    print('Building template release assets completed.')


if __name__ == '__main__':
    build_template_release()
