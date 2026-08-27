from model import deepseek
import asyncio



SIMPLE_KEYWORDS = [
    'hello world', '单文件', '一个函数', '一个脚本',
    '输出', '打印', '计算器', '爬虫', '小工具'
]

COMPLEX_KEYWORDS = [
    '系统', '平台', '多个模块', '前后端', '数据库',
    '登录', '权限', '部署', '微服务', 'API', '管理后台'
]
REQUIREMENT = input('>>> ')
ARCHI_RESULT = []
STRUCTURE_RESULT = REQUIREMENT
TASKS_RESULT = ''

ARCHI_STRUCTURE = '''
{{
  "Functional": [
    {"id":"Re-1", "description":"需求描述", "priority":"High/Medium/Low"},
    {"id":"Re-2", "description":"需求描述", "priority":"High/Medium/Low"},
    ...
  ],
  "Non-functional": [
    {"id":'nRe-1', "type":"需求类型", "description":"需求描述"},
    {"id":"nRe-2", "type":"需求类型", "description":"需求描述"},
    ...
  ],
  "Issues" : [
    {"id":"is-1", "description":"问题描述", "priority":"High/Medium/Low"},
    {"id":"is-2", "description":"问题描述", "priority":"High/Medium/Low"},
    ...
  ]
}}
'''
ARCHI_PROMPT = f"""
你是一个需求分析专家。请分析用户的需求，输出结构化的需求文档。不要用markdown格式。

## 任务列表：
1.识别所有功能需求
2.识别非功能需求（性能、安全、可用性等）
3.标注模糊点（如果需求不清晰，列出需要澄清的问题）
4.输出结构化json
           
## 用户需求：{REQUIREMENT}

## 输出格式：{ARCHI_STRUCTURE}

只输出JSON，不要输出任何解释、前言或总结。
"""
EXTRA_ARCHI_PROMPT = """
## 重要约束：
- 如果需求简单（如单文件脚本），功能需求不超过3条
- 非功能需求只列真正必要的，不超过3条
- issues只列会影响代码正确性的问题，不超过2条
- 不要过度分析
"""


STRUCTURE_STR = """
{{
  "tech_stack": {{
    "language": "使用的编程语言 (如python)",
    "framework": "使用的框架 (如fastapi)",
    "database": "数据存储工具 (如sqlite)",
    "reasoning": "选择理由"
  }},
  "directory_structure": [
    "src/...",
    "src/...",
    ".../...",
    ...
  ],
  "modules": [
    {{
      "name": "模块名",
      "responsibility": "用户相关业务逻辑",
      "depends_on": ["依赖的模块1", "依赖的模块2"...],
      "provides": ["提供的模块1", "提供的模块2"...]
    }}
  ],
  "data_flow": "数据流 (用英文逗号连接)",
  "design_decisions": [
    {{
      "decision": "设计思路",
      "reason": "原因",
      "rejection_reason": "原因"
    }}
  ]
}}
"""
STRUCTURE_PROMPT = f"""
你是一个资深软件架构师。请根据以下需求，为用户设计完整的技术方案。不要用markdown格式。

## 用户需求：{ARCHI_RESULT}

## 任务列表：
1. 选择技术栈并说明理由
2. 设计项目目录结构
3. 划分模块并定义职责
4. 设计模块间接口规范
5. 设计数据流

## 输出格式：{STRUCTURE_STR}

只输出JSON，不要输出任何解释、前言或总结。
"""


TASKS_STRUCTURE = """
{{
  "Tasks": [
    {{
      "id": "t1",
      "language": "使用的语言",
      "description": "任务描述",
      "depend": [依赖的子任务1, 依赖的子任务2...]
      "output_file": "此任务在哪个文件内实现 (如src/a.py)"
      "interface": {{
        "provides": "提供了什么接口",
        "input": "输入什么 (如果没有，比如定义类任务，就填“无”)
        "output": "输出什么"
      }}
    }},
    {{
      "id": "t2",
      "language": "使用的语言",
      "description": "任务描述",
      "depend": [依赖的子任务1, 依赖的子任务2...]
      "output_file": "此任务在哪个文件内实现 (如src/b.py)"
      "interface": {{
        "provides": "提供了什么接口",
        "input": "输入什么 (如果没有，比如定义类任务，就填“无”)
        "output": "输出什么"
      }}
    }},
    ...
  ]
}}
"""
TASKS_PROMPT = f"""
你是一个任务规划专家。请将以下架构方案拆分为可执行的子任务。不要用markdown格式。

## 架构方案：{STRUCTURE_RESULT}

## 任务列表：
1. 拆分子任务，粒度适中 (每个任务一个文件或一个模块)
2. 标注任务间依赖关系
3. 为每个任务定义输入输出接口
4. 输出依赖图

## 输出格式：{TASKS_STRUCTURE}
"""


CODING_PROMPT = f"""
你是一个专业程序员。请根据以下任务描述生成完整可运行的代码。不要使用markdown格式。

## 任务描述：{REQUIREMENT}

## 
"""


def complexity_judge(requirement: str) -> str:
    if len(requirement) >= 30:
        hits = sum(1 for kw in COMPLEX_KEYWORDS if kw in requirement)
        if hits >= 2:
            return 'complex'
        elif hits == 1:
            return 'medium'
    return 'simple'

if __name__ == "__main__":
    archi = deepseek.Archi(name="archi", base_url="", api_key="")
    if complexity_judge(REQUIREMENT) != 'simple':
        if complexity_judge(REQUIREMENT) == 'complex':
            archi_result = archi.call(ARCHI_PROMPT)
        else:
            archi_result = archi.call(ARCHI_PROMPT+EXTRA_ARCHI_PROMPT)
        STRUCTURE_STR = {'功能性需求':archi_result['Functional'],
                         '非功能性需求':archi_result['Non-functional'],
                         '需要注意的问题':archi_result['Issues'],}
        print(f'需求分析：\n{archi_result[1]}\n结构参考：{STRUCTURE_STR}')

    STRUCTURE_RESULT = REQUIREMENT
    print(TASKS_PROMPT)
    tasks_result = archi.call(TASKS_PROMPT)
    print(tasks_result[1])


