#!/usr/bin/env python3
"""
颜色输出工具模块 - by 阮阮
提供统一的控制台颜色输出功能，支持多种消息类型和兼容性选项
"""

import os
import sys
from enum import Enum
from typing import Optional, Union


class MessageType(Enum):
    """消息类型枚举"""
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    INFO = "INFO"
    NORMAL = "NORMAL"
    DEBUG = "DEBUG"
    PROGRESS = "PROGRESS"


class ColorCodes:
    """ANSI颜色代码"""
    # 基础颜色
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'  # 256色模式的橙色
    GRAY = '\033[90m'  # 深灰色
    
    # 高级颜色（256色模式）
    LIGHT_BLUE = '\033[38;5;117m'  # 浅蓝色
    LIGHT_GREEN = '\033[38;5;120m'  # 浅绿色
    PINK = '\033[38;5;213m'  # 粉色
    DARK_GREEN = '\033[38;5;34m'  # 深绿色
    
    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_DARK_GRAY = '\033[48;5;236m'  # 深灰背景
    BG_BLUE = '\033[44m'
    BG_LIGHT_GRAY = '\033[48;5;240m'  # 浅灰背景
    
    # 荧光笔效果背景色（明亮且柔和）
    BG_HIGHLIGHT_BLUE = '\033[48;5;24m'      # 深蓝荧光笔
    BG_HIGHLIGHT_GREEN = '\033[48;5;22m'     # 深绿荧光笔  
    BG_HIGHLIGHT_YELLOW = '\033[48;5;220m'   # 黄色荧光笔
    BG_HIGHLIGHT_PINK = '\033[48;5;199m'     # 粉色荧光笔
    BG_HIGHLIGHT_PURPLE = '\033[48;5;93m'    # 紫色荧光笔
    BG_HIGHLIGHT_CYAN = '\033[48;5;30m'      # 青色荧光笔
    
    # AI回复专用荧光笔背景（柔和的蓝绿色）
    BG_AI_RESPONSE = '\033[48;5;24m'         # AI回复背景
    TEXT_AI_RESPONSE = '\033[97m'            # AI回复文字（亮白色）
    
    # 重置
    RESET = '\033[0m'
    
    # 颜色映射
    TYPE_COLORS = {
        MessageType.ERROR: RED,
        MessageType.SUCCESS: GREEN,
        MessageType.WARNING: YELLOW,
        MessageType.INFO: BLUE,
        MessageType.NORMAL: WHITE,
        MessageType.DEBUG: PURPLE,
        MessageType.PROGRESS: ORANGE,
    }
    
    # 代码高亮配色
    CODE_COLORS = {
        'keyword': PURPLE + BOLD,      # 关键字：粗体紫色
        'string': GREEN,               # 字符串：绿色
        'number': CYAN,                # 数字：青色
        'comment': GRAY + ITALIC,      # 注释：斜体灰色
        'function': LIGHT_BLUE,        # 函数：浅蓝色
        'class': YELLOW + BOLD,        # 类名：粗体黄色
        'operator': WHITE,             # 操作符：白色
        'builtin': PINK,               # 内置函数：粉色
        'variable': WHITE,             # 变量：白色
        'background': BG_DARK_GRAY,    # 代码块背景：深灰色
    }


class ColorConfig:
    """颜色配置类"""
    def __init__(self):
        self.enabled = self._should_enable_colors()
        self.force_disable = False
        
    def _should_enable_colors(self) -> bool:
        """检测是否应该启用颜色输出"""
        # 检查环境变量
        if os.getenv('NO_COLOR'):
            return False
        if os.getenv('FORCE_COLOR'):
            return True
            
        # 检查终端支持
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
            
        # 检查TERM环境变量
        term = os.getenv('TERM', '')
        if term in ('dumb', 'unknown'):
            return False
            
        # macOS终端通常支持颜色
        if sys.platform == 'darwin':
            return True
            
        # 其他Unix系统的基本检查
        return term != ''
    
    def disable_colors(self):
        """禁用颜色输出"""
        self.force_disable = True
        
    def enable_colors(self):
        """启用颜色输出"""
        self.force_disable = False
        
    def is_enabled(self) -> bool:
        """检查颜色是否启用"""
        return self.enabled and not self.force_disable


# 全局配置实例
_color_config = ColorConfig()


def colored_print(
    message: str,
    msg_type: Union[MessageType, str] = MessageType.NORMAL,
    prefix: Optional[str] = None,
    end: str = '\n',
    flush: bool = False,
    file=None
) -> None:
    """
    统一的颜色输出函数
    
    Args:
        message: 要输出的消息内容
        msg_type: 消息类型，可以是MessageType枚举或字符串
        prefix: 自定义前缀，如果为None则使用默认格式 [类型]
        end: 行结束符，默认为换行
        flush: 是否立即刷新输出缓冲区
        file: 输出文件对象，默认为sys.stdout
    """
    if file is None:
        file = sys.stdout
        
    # 处理字符串类型的msg_type
    if isinstance(msg_type, str):
        try:
            msg_type = MessageType(msg_type.upper())
        except ValueError:
            msg_type = MessageType.NORMAL
    
    # 构建输出内容
    if _color_config.is_enabled():
        color = ColorCodes.TYPE_COLORS.get(msg_type, ColorCodes.WHITE)

        if prefix is None:
            # 使用默认格式 [类型] 消息内容 - 整个消息都有颜色
            formatted_message = f"{color}[{msg_type.value}] {message}{ColorCodes.RESET}"
        else:
            # 使用自定义前缀 - 整个消息都有颜色
            formatted_message = f"{color}{prefix} {message}{ColorCodes.RESET}"
    else:
        # 无颜色模式
        if prefix is None:
            formatted_message = f"[{msg_type.value}] {message}"
        else:
            formatted_message = f"{prefix} {message}"
    
    print(formatted_message, end=end, flush=flush, file=file)


def print_error(message: str, **kwargs) -> None:
    """输出错误信息"""
    colored_print(message, MessageType.ERROR, **kwargs)


def print_success(message: str, **kwargs) -> None:
    """输出成功信息"""
    colored_print(message, MessageType.SUCCESS, **kwargs)


def print_warning(message: str, **kwargs) -> None:
    """输出警告信息"""
    colored_print(message, MessageType.WARNING, **kwargs)


def print_info(message: str, **kwargs) -> None:
    """输出信息提示"""
    colored_print(message, MessageType.INFO, **kwargs)


def print_debug(message: str, **kwargs) -> None:
    """输出调试信息"""
    colored_print(message, MessageType.DEBUG, **kwargs)


def print_progress(message: str, **kwargs) -> None:
    """输出进度状态"""
    colored_print(message, MessageType.PROGRESS, **kwargs)


def disable_colors() -> None:
    """全局禁用颜色输出"""
    _color_config.disable_colors()


def enable_colors() -> None:
    """全局启用颜色输出"""
    _color_config.enable_colors()


def is_colors_enabled() -> bool:
    """检查颜色输出是否启用"""
    return _color_config.is_enabled()


def format_code_block(code: str, language: str = "python") -> str:
    """
    格式化代码块，添加语法高亮和背景
    
    Args:
        code: 要格式化的代码内容
        language: 编程语言，默认为python
        
    Returns:
        格式化后的代码字符串
    """
    if not _color_config.is_enabled():
        return code
        
    import re
    
    # 代码块背景和边框
    bg_color = ColorCodes.CODE_COLORS['background']
    reset = ColorCodes.RESET
    
    # 根据语言进行语法高亮
    if language.lower() in ('python', 'py'):
        code = _highlight_python(code)
    elif language.lower() in ('javascript', 'js', 'typescript', 'ts'):
        code = _highlight_javascript(code)
    elif language.lower() in ('bash', 'shell', 'sh'):
        code = _highlight_bash(code)
    elif language.lower() in ('sql'):
        code = _highlight_sql(code)
    else:
        # 通用高亮
        code = _highlight_generic(code)
    
    # 添加背景和边框
    lines = code.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():  # 非空行添加背景
            formatted_line = f"{bg_color} {line.ljust(80)} {reset}"
        else:  # 空行
            formatted_line = f"{bg_color}{' ' * 82}{reset}"
        formatted_lines.append(formatted_line)
    
    return '\n'.join(formatted_lines)


def _highlight_python(code: str) -> str:
    """Python语法高亮"""
    import re
    
    # Python关键字
    keywords = r'\b(def|class|if|elif|else|for|while|try|except|finally|with|as|import|from|return|yield|lambda|and|or|not|in|is|None|True|False|pass|break|continue|global|nonlocal|assert|del|raise|async|await)\b'
    
    # 字符串（支持三引号和单双引号）
    strings = r'("""[^"]*"""|\'\'\'[^\']*\'\'\'|"[^"]*"|\'[^\']*\')'
    
    # 数字
    numbers = r'\b(\d+\.?\d*|\.\d+)\b'
    
    # 注释
    comments = r'(#.*$)'
    
    # 函数调用
    functions = r'\b(\w+)(?=\s*\()'
    
    # 类名（大写开头）
    classes = r'\b([A-Z]\w*)\b'
    
    # 内置函数
    builtins = r'\b(print|len|str|int|float|list|dict|set|tuple|range|enumerate|zip|map|filter|open|input|type|isinstance|hasattr|getattr|setattr|super|staticmethod|classmethod|property)\b'
    
    # 应用高亮
    code = re.sub(keywords, lambda m: f"{ColorCodes.CODE_COLORS['keyword']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(strings, lambda m: f"{ColorCodes.CODE_COLORS['string']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(numbers, lambda m: f"{ColorCodes.CODE_COLORS['number']}{m.group(0)}{ColorCodes.RESET}", code)
    code = re.sub(comments, lambda m: f"{ColorCodes.CODE_COLORS['comment']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(builtins, lambda m: f"{ColorCodes.CODE_COLORS['builtin']}{m.group(0)}{ColorCodes.RESET}", code)
    code = re.sub(functions, lambda m: f"{ColorCodes.CODE_COLORS['function']}{m.group(1)}{ColorCodes.RESET}", code)
    code = re.sub(classes, lambda m: f"{ColorCodes.CODE_COLORS['class']}{m.group(0)}{ColorCodes.RESET}", code)
    
    return code


def _highlight_javascript(code: str) -> str:
    """JavaScript/TypeScript语法高亮"""
    import re
    
    keywords = r'\b(var|let|const|function|class|if|else|for|while|do|switch|case|default|try|catch|finally|throw|return|break|continue|typeof|instanceof|new|this|super|extends|import|export|from|async|await|yield|true|false|null|undefined)\b'
    strings = r'(`[^`]*`|"[^"]*"|\'[^\']*\')'
    numbers = r'\b(\d+\.?\d*|\.\d+)\b'
    comments = r'(//.*$|/\*[\s\S]*?\*/)'
    functions = r'\b(\w+)(?=\s*\()'
    
    code = re.sub(keywords, lambda m: f"{ColorCodes.CODE_COLORS['keyword']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(strings, lambda m: f"{ColorCodes.CODE_COLORS['string']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(numbers, lambda m: f"{ColorCodes.CODE_COLORS['number']}{m.group(0)}{ColorCodes.RESET}", code)
    code = re.sub(comments, lambda m: f"{ColorCodes.CODE_COLORS['comment']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(functions, lambda m: f"{ColorCodes.CODE_COLORS['function']}{m.group(1)}{ColorCodes.RESET}", code)
    
    return code


def _highlight_bash(code: str) -> str:
    """Bash/Shell语法高亮"""
    import re
    
    keywords = r'\b(if|then|else|elif|fi|for|while|do|done|case|esac|function|return|break|continue|exit|export|source|alias|unalias|cd|pwd|echo|printf)\b'
    strings = r'("[^"]*"|\'[^\']*\')'
    comments = r'(#.*$)'
    variables = r'(\$\w+|\$\{[^}]+\})'
    
    code = re.sub(keywords, lambda m: f"{ColorCodes.CODE_COLORS['keyword']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(strings, lambda m: f"{ColorCodes.CODE_COLORS['string']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(comments, lambda m: f"{ColorCodes.CODE_COLORS['comment']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(variables, lambda m: f"{ColorCodes.CODE_COLORS['variable']}{m.group(0)}{ColorCodes.RESET}", code)
    
    return code


def _highlight_sql(code: str) -> str:
    """SQL语法高亮"""
    import re
    
    keywords = r'\b(SELECT|FROM|WHERE|JOIN|INNER|LEFT|RIGHT|FULL|OUTER|ON|GROUP|BY|HAVING|ORDER|ASC|DESC|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|ALTER|DROP|INDEX|DATABASE|PRIMARY|KEY|FOREIGN|REFERENCES|CONSTRAINT|NULL|NOT|AND|OR|LIKE|IN|EXISTS|BETWEEN|UNION|ALL|DISTINCT|COUNT|SUM|AVG|MAX|MIN)\b'
    strings = r'(\'[^\']*\')'
    numbers = r'\b(\d+\.?\d*|\.\d+)\b'
    comments = r'(--.*$|/\*[\s\S]*?\*/)'
    
    code = re.sub(keywords, lambda m: f"{ColorCodes.CODE_COLORS['keyword']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE | re.IGNORECASE)
    code = re.sub(strings, lambda m: f"{ColorCodes.CODE_COLORS['string']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(numbers, lambda m: f"{ColorCodes.CODE_COLORS['number']}{m.group(0)}{ColorCodes.RESET}", code)
    code = re.sub(comments, lambda m: f"{ColorCodes.CODE_COLORS['comment']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    
    return code


def _highlight_generic(code: str) -> str:
    """通用语法高亮"""
    import re
    
    # 简单的通用规则
    strings = r'("[^"]*"|\'[^\']*\'|`[^`]*`)'
    numbers = r'\b(\d+\.?\d*|\.\d+)\b'
    comments = r'(//.*$|#.*$|/\*[\s\S]*?\*/)'
    
    code = re.sub(strings, lambda m: f"{ColorCodes.CODE_COLORS['string']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    code = re.sub(numbers, lambda m: f"{ColorCodes.CODE_COLORS['number']}{m.group(0)}{ColorCodes.RESET}", code)
    code = re.sub(comments, lambda m: f"{ColorCodes.CODE_COLORS['comment']}{m.group(0)}{ColorCodes.RESET}", code, flags=re.MULTILINE)
    
    return code


def create_highlighted_text(text: str, bg_color: str = None, text_color: str = None, fill_width: int = None) -> str:
    """
    创建带荧光笔效果的高亮文本
    
    Args:
        text: 要高亮的文本
        bg_color: 背景色，默认使用AI回复背景色
        text_color: 文字色，默认使用AI回复文字色
        fill_width: 填充宽度，None表示不填充
        
    Returns:
        格式化后的高亮文本
    """
    if not _color_config.is_enabled():
        return text
        
    if bg_color is None:
        bg_color = ColorCodes.BG_AI_RESPONSE
    if text_color is None:
        text_color = ColorCodes.TEXT_AI_RESPONSE
        
    reset = ColorCodes.RESET
    
    if fill_width:
        # 填充模式：确保每行都有完整的背景色
        lines = text.split('\n')
        highlighted_lines = []
        
        for line in lines:
            # 计算实际显示宽度（排除ANSI代码）
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            display_width = len(clean_line)
            
            # 填充到指定宽度
            padding = ' ' * max(0, fill_width - display_width)
            highlighted_line = f"{bg_color}{text_color}{line}{padding}{reset}"
            highlighted_lines.append(highlighted_line)
            
        return '\n'.join(highlighted_lines)
    else:
        # 简单模式：只给文本内容添加背景
        return f"{bg_color}{text_color}{text}{reset}"


def create_ai_response_highlight(text: str, terminal_width: int = 80) -> str:
    """
    为AI回复创建荧光笔高亮效果
    
    Args:
        text: AI回复文本
        terminal_width: 终端宽度
        
    Returns:
        高亮格式化的文本
    """
    if not _color_config.is_enabled():
        return text
        
    # 使用柔和的蓝色背景和亮白色文字
    return create_highlighted_text(text, 
                                 ColorCodes.BG_AI_RESPONSE, 
                                 ColorCodes.TEXT_AI_RESPONSE, 
                                 terminal_width - 2)  # 减2为边距


def create_streaming_highlight_chunk(chunk: str, is_first_chunk: bool = False, is_last_chunk: bool = False) -> str:
    """
    为流式输出的每个chunk创建高亮效果
    适配逐字符输出，确保背景色连续
    
    Args:
        chunk: 当前输出的文本片段
        is_first_chunk: 是否是第一个chunk
        is_last_chunk: 是否是最后一个chunk
        
    Returns:
        带高亮效果的chunk
    """
    if not _color_config.is_enabled():
        return chunk
        
    bg_color = ColorCodes.BG_AI_RESPONSE
    text_color = ColorCodes.TEXT_AI_RESPONSE
    reset = ColorCodes.RESET
    
    # 为每个字符添加背景色，确保连续性
    if chunk == '\n':
        # 换行符需要特殊处理，确保到行尾都有背景色，然后换行后继续背景
        return f"{' ' * 2}{reset}\n{bg_color}{text_color}"
    elif chunk in [' ', '\t']:
        # 空白字符保持背景色
        return f"{bg_color}{text_color}{chunk}"
    else:
        # 普通字符，添加背景和文字色
        if is_first_chunk:
            # 第一个chunk开始背景色
            formatted_chunk = f"{bg_color}{text_color}{chunk}"
        else:
            # 后续chunk，假设已经在背景色状态中
            formatted_chunk = chunk
            
        # 如果是最后一个chunk，添加重置
        if is_last_chunk:
            formatted_chunk += reset
            
        return formatted_chunk


def create_response_border(width: int = 80, style: str = "ai") -> tuple:
    """
    创建AI回复的视觉边界
    
    Args:
        width: 边界宽度
        style: 边界样式 ("ai", "code", "simple")
        
    Returns:
        (顶部边界, 底部边界) 元组
    """
    if not _color_config.is_enabled():
        return ("", "")
        
    if style == "ai":
        # AI回复样式：使用荧光笔背景色
        bg = ColorCodes.BG_AI_RESPONSE
        reset = ColorCodes.RESET
        
        top_border = f"{bg}{' ' * width}{reset}"
        bottom_border = f"{bg}{' ' * width}{reset}"
        
        return (top_border, bottom_border)
        
    elif style == "code":
        # 代码样式：使用框线字符
        border_color = ColorCodes.CYAN
        reset = ColorCodes.RESET
        
        top_border = f"{border_color}┌{'─' * (width-2)}┐{reset}"
        bottom_border = f"{border_color}└{'─' * (width-2)}┘{reset}"
        
        return (top_border, bottom_border)
        
    else:
        # 简单样式
        border_color = ColorCodes.GRAY
        reset = ColorCodes.RESET
        
        top_border = f"{border_color}{'─' * width}{reset}"
        bottom_border = f"{border_color}{'─' * width}{reset}"
        
        return (top_border, bottom_border)


def detect_and_format_code(text: str) -> str:
    """
    检测文本中的代码块并格式化
    支持Markdown风格的代码块：```language 和 ```
    
    Args:
        text: 包含可能代码块的文本
        
    Returns:
        格式化后的文本
    """
    if not _color_config.is_enabled():
        return text
        
    import re
    
    # 匹配代码块模式：```language 代码内容 ```
    code_block_pattern = r'```(\w*)\n?(.*?)\n?```'
    
    def replace_code_block(match):
        language = match.group(1) or 'generic'
        code_content = match.group(2)
        
        if not code_content.strip():
            return match.group(0)  # 空代码块不处理
            
        # 格式化代码块
        formatted_code = format_code_block(code_content, language)
        
        # 添加代码块标识和边框
        header = f"{ColorCodes.GRAY}┌─ {language.upper() if language != 'generic' else 'CODE'} ─{'─' * (73 - len(language))}┐{ColorCodes.RESET}"
        footer = f"{ColorCodes.GRAY}└{'─' * 80}┘{ColorCodes.RESET}"
        
        return f"\n{header}\n{formatted_code}\n{footer}\n"
    
    # 替换所有代码块
    formatted_text = re.sub(code_block_pattern, replace_code_block, text, flags=re.DOTALL)
    
    # 处理行内代码（用反引号包围的代码）
    inline_code_pattern = r'`([^`]+)`'
    
    def replace_inline_code(match):
        code = match.group(1)
        return f"{ColorCodes.CODE_COLORS['background']} {ColorCodes.CYAN}{code}{ColorCodes.RESET}{ColorCodes.CODE_COLORS['background']} {ColorCodes.RESET}"
    
    formatted_text = re.sub(inline_code_pattern, replace_inline_code, formatted_text)
    
    return formatted_text


def demo() -> None:
    """演示所有颜色类型"""
    print("颜色输出演示:")
    print("-" * 50)
    
    print_error("这是错误信息")
    print_success("这是成功信息")
    print_warning("这是警告信息")
    print_info("这是信息提示")
    colored_print("这是普通文本", MessageType.NORMAL)
    print_debug("这是调试信息")
    print_progress("这是进度状态")
    
    print("-" * 50)
    print("自定义前缀示例:")
    colored_print("自定义前缀消息", MessageType.INFO, prefix="[自定义]")
    
    print("-" * 50)
    print(f"颜色支持状态: {'启用' if is_colors_enabled() else '禁用'}")


if __name__ == "__main__":
    demo()
