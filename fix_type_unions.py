#!/usr/bin/env python3
"""修复Python 3.9兼容性问题：将类型联合语法从 A | B 改为 Union[A, B]"""

import os
import re
from pathlib import Path

def fix_type_unions(content: str) -> str:
    """将 | 类型联合语法改为 Union"""
    # 匹配函数参数或返回值中的类型联合
    # 例如: int | float -> Union[int, float]
    # 例如: list[dict] | None -> Optional[list[dict]]
    
    lines = content.split('\n')
    result = []
    has_union = False
    has_optional = False
    
    for line in lines:
        # 跳过注释行
        if '# Python 3.12' in line:
            result.append(line)
            continue
        
        # 匹配 -> Type | None (Optional)
        if '->' in line and '| None' in line:
            match = re.search(r'->\s*([a-zA-Z_\[\],\s]+)\s*\|\s*None', line)
            if match:
                type_str = match.group(1).strip()
                line = line.replace(f'-> {type_str} | None', f'-> Optional[{type_str}]')
                line = line.replace(f'->{type_str}|None', f'->Optional[{type_str}]')
                has_optional = True
        
        # 匹配参数中的 Type | None (Optional)
        elif '|' in line and 'None' in line and ':' in line:
            match = re.search(r':\s*([a-zA-Z_\[\],\s]+)\s*\|\s*None', line)
            if match:
                type_str = match.group(1).strip()
                line = line.replace(f': {type_str} | None', f': Optional[{type_str}]')
                line = line.replace(f':{type_str}|None', f':Optional[{type_str}]')
                has_optional = True
        
        # 匹配其他类型联合 (Union)
        elif '|' in line and ('def ' in line or ':' in line):
            # 简单的类型联合，如 int | float
            match = re.search(r'([a-zA-Z_]\w*)\s*\|\s*([a-zA-Z_]\w*)', line)
            if match and 'MARKET' not in line:  # 避免修改枚举
                type1 = match.group(1)
                type2 = match.group(2)
                if type1 != 'None' and type2 != 'None':
                    line = line.replace(f'{type1} | {type2}', f'Union[{type1}, {type2}]')
                    line = line.replace(f'{type1}|{type2}', f'Union[{type1}, {type2}]')
                    has_union = True
        
        result.append(line)
    
    # 如果有Union或Optional，需要添加导入
    if has_union or has_optional:
        # 查找from typing import行
        for i, line in enumerate(result):
            if 'from typing import' in line:
                imports = []
                if 'Union' not in line and has_union:
                    imports.append('Union')
                if 'Optional' not in line and has_optional:
                    imports.append('Optional')
                
                if imports:
                    # 在现有导入中添加
                    if line.rstrip().endswith(')'):
                        # 多行导入，简单处理：在前面插入
                        result.insert(i, f"from typing import {', '.join(imports)}")
                    else:
                        # 单行导入
                        result[i] = line.rstrip() + f", {', '.join(imports)}"
                break
    
    return '\n'.join(result)

def process_file(file_path: Path):
    """处理单个Python文件"""
    print(f"Processing {file_path}")
    
    try:
        content = file_path.read_text()
        fixed_content = fix_type_unions(content)
        
        if content != fixed_content:
            file_path.write_text(fixed_content)
            print(f"  ✅ Fixed: {file_path}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    """批量处理所有Python文件"""
    base_path = Path.home() / 'Documents' / 'pytdx2' / 'tdx_mcp'
    
    for py_file in base_path.rglob('*.py'):
        process_file(py_file)
    
    print("\n✅ Done!")

if __name__ == '__main__':
    main()
