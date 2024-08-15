import json
import sys
import time
from io import StringIO
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from auto_unpack.util import file

config_dir: Path = Path('config')
examples_dir: Path = Path('docs/page/examples')
schema_path: Path = Path('schema/examples-schema.json')

example_template = """# {title}

!!! note "场景介绍"

    {description}
    
{docs}

## 处理流程

```yaml
{yaml}
```
"""


class ConfigMeta(BaseModel):
    """
    配置文件元数据，用于生成示例文档
    """
    example_doc: bool = Field(
        default=False,
        description="是否生成示例文档"
    )
    title: str = Field(
        default="",
        description="示例标题"
    )
    description: str = Field(
        default="",
        description="示例描述"
    )
    docs: str = Field(
        default="",
        description="示例补充文档"
    )


def build_example_docs():
    """
    构建示例文档
    """
    # 清理旧文档
    for f in examples_dir.glob('*.md'):
        f.unlink()

    # 获取配置文档
    flow_files: List[Path] = list(config_dir.glob('application.*.yaml'))

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True

    for flow_file in flow_files:
        try:
            flow_file_yaml: CommentedMap = yaml.load(file.read_file(flow_file))
            config_meta = ConfigMeta.model_validate(flow_file_yaml)

            if not config_meta.example_doc:
                continue

            # 删除配置字段
            for f in ConfigMeta.model_fields.keys():
                if f in flow_file_yaml:
                    del flow_file_yaml[f]

            string_stream = StringIO()
            yaml.dump(flow_file_yaml, string_stream)
            flow_file_content = string_stream.getvalue()

            example_context = example_template.format(
                title=config_meta.title,
                docs=config_meta.docs,
                description=config_meta.description,
                yaml=flow_file_content,
            )

            name = flow_file.stem.replace('application.', '')
            example_file = examples_dir / f"{name}.md"

            file.write_file(example_file, example_context)

            print(f"Create example file: {example_file}")
        except:
            pass


class FileWatcherHandler(FileSystemEventHandler):
    """
    文件监控事件处理器
    """

    def on_modified(self, event: FileSystemEvent) -> None:
        print(f"File {event.src_path} was modified")
        build_example_docs()

    def on_created(self, event: FileSystemEvent) -> None:
        print(f"File {event.src_path} was created")
        build_example_docs()

    def on_deleted(self, event: FileSystemEvent) -> None:
        print(f"File {event.src_path} was deleted")
        build_example_docs()


def main():
    """
    主函数
    """
    argv_len = len(sys.argv)
    if argv_len > 1 and sys.argv[1] in ['-s', '--schema']:
        print("Generate schema file.")
        schema = json.dumps(ConfigMeta.model_json_schema(),
                            ensure_ascii=False, indent=4)
        file.write_file(schema_path, schema)
        print(f"Schema file was generated: {schema_path}")
        return

    watch = argv_len > 1 and sys.argv[1] in ['-w', '--watch']

    print("Start generate examples docs.")
    build_example_docs()
    if watch:
        file_watcher = FileWatcherHandler()
        observer = Observer()
        observer.schedule(file_watcher, str(config_dir), recursive=True)
        observer.start()
        print("Watching file changes...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    print("Generate examples docs done.")


if __name__ == '__main__':
    main()
