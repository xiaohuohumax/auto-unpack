from pathlib import Path
import re
from typing import List

from auto_unpack.util import file

config_dir: Path = Path('config')
examples_dir: Path = Path('docs/page/examples')

example_template = """# {title}

!!! note "场景介绍"

    {description}

## 处理流程

```yaml
{yaml}
```
"""

if __name__ == '__main__':
    # 清理旧文档
    for f in examples_dir.glob('*.md'):
        f.unlink()

    # 获取配置文档
    flow_files: List[Path] = list(config_dir.glob('application.*.yaml'))
    print("Start generate examples docs.")

    title_re = r'#\s*title:\s*(.*)\n'
    description_re = r'#\s*description:\s*(.*)\n'

    for flow_file in flow_files:
        flow_file_content = file.read_file(flow_file)

        titles = re.findall(title_re, flow_file_content)
        descriptions = re.findall(description_re, flow_file_content)

        if len(titles) != 1 or len(descriptions) != 1:
            continue

        title = titles[-1]
        description = descriptions[-1]

        example_context = example_template.format(
            title=title,
            description=description,
            yaml=flow_file_content
        )
        name = flow_file.stem.replace('application.', '')
        example_file = examples_dir / f"{name}.md"

        example_context = re.sub(title_re, '', example_context)
        example_context = re.sub(description_re, '', example_context)

        file.write_file(example_file, example_context)

        print(f"Create example file: {example_file}")

    print("Generate examples docs done.")
