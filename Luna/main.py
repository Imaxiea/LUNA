from model import deepseek
import asyncio
from collections import deque
from pathlib import Path



ai = deepseek.Use(name="archi", base_url="", api_key="")
SIMPLE_KEYWORDS = [
    'hello world', '单文件', '一个函数', '一个脚本',
    '输出', '打印', '计算器', '爬虫', '小工具'
]

COMPLEX_KEYWORDS = [
    '系统', '平台', '多个模块', '前后端', '数据库',
    '登录', '权限', '部署', '微服务', 'API', '管理后台'
]
REQUIREMENT = input('>>> ')


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

def archi(complexity:int=1):
    if complexity == 1:
        result = ai.call(ARCHI_PROMPT+EXTRA_ARCHI_PROMPT)
    else:
        result = ai.call(ARCHI_PROMPT)
    return result

def structure(archi_result):
    STRUCTURE_PROMPT = f"""
    你是一个资深软件架构师。请根据以下需求，为用户设计完整的技术方案。不要用markdown格式。

    ## 用户需求：{archi_result}

    ## 任务列表：
    1. 选择技术栈并说明理由
    2. 设计项目目录结构
    3. 划分模块并定义职责
    4. 设计模块间接口规范
    5. 设计数据流

    ## 输出格式：{STRUCTURE_STR}

    只输出JSON，不要输出任何解释、前言或总结。
    """
    result = ai.call(STRUCTURE_PROMPT)
    return result

def taskdispatch(structure_result):
    TASKS_PROMPT = f"""
    你是一个任务规划专家。请将以下架构方案拆分为可执行的子任务。不要用markdown格式。

    ## 架构方案：{structure_result}

    ## 任务列表：
    1. 拆分子任务，粒度适中 (每个任务一个文件或一个模块)
    2. 标注任务间依赖关系
    3. 为每个任务定义输入输出接口
    4. 输出依赖图

    ## 输出格式：{TASKS_STRUCTURE}
    """
    result = ai.call(TASKS_PROMPT)
    return result

class Dispatcher:
    def __init__(self, tasks, architecture):
        self.tasks = {t["id"]: t for t in tasks}
        self.completed = {}
        self.architecture = architecture
        self.pending = deque()

    def get_ready_tasks(self):
        ready = []
        for t in self.tasks.values():
            if t["id"] in self.completed:
                continue
            if all(dep in self.completed for dep in t["dependencies"]):
                ready.append(t)
        return ready

    def get_dependency_context(self, task):
        if not task["dependencies"]:
            return "None"

        context_lines = []
        for dep_id in task["dependencies"]:
            dep = self.completed[dep_id]
            context_lines.append(f"""
                                 ### {dep_id}（来自 {dep['file']}）
                                 提供接口：
                                 {dep['interface']}
                                 """)
        return "\n".join(context_lines)

    def get_relevant_constraints(self, task):
        language = task["language"]
        file_path = task["output_file"]

        relevant = []

        tech_stack = self.architecture.get("tech_stack", {})
        if language in tech_stack:
            relevant.append(f"目标语言: {language}")
            relevant.append(f"约束: {tech_stack[language]}")

        modules = self.architecture.get("modules", [])
        for module in modules:
            if module.get("name", "").lower() in file_path.lower():
                relevant.append(f"模块职责: {module['responsibility']}")
                relevant.append(f"依赖: {module.get('depends_on', [])}")
                relevant.append(f"提供: {module.get('provides', [])}")

        decisions = self.architecture.get("design_decisions", [])
        for decision in decisions:
            if language in decision.get("decision", "").lower():
                relevant.append(f"设计决策: {decision['decision']} - {decision['reason']}")

        if not relevant:
            return "遵循语言标准规范"

        return "\n".join(relevant)

    def run(self):
        while len(self.completed) < len(self.tasks):
            ready = self.get_ready_tasks()

            if not ready:
                raise RuntimeError("存在循环依赖或依赖无法满足")

            for task in ready:
                self.execute_task(task)

        return self.completed

    def execute_task(self, task):
        dependency_context = self.get_dependency_context(task)
        constraints = self.get_relevant_constraints(task)

        prompt = self.build_code_gen_prompt(
            task=task,
            dependency_context=dependency_context,
            constraints=constraints
        )

        code = ai.call(prompt)

        self.completed[task["id"]] = {
            "file": task["output_file"],
            "interface": task["interface"]["provides"],
            "code": code
        }

    def save_files(self, output_dir="output"):
        for task_id, task_info in self.completed.items():
            file_path = Path(output_dir) / task_info["file"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(task_info["code"], encoding="utf-8")
            print(f"已保存: {file_path}")

    @staticmethod
    def build_code_gen_prompt(task, dependency_context, constraints):
        return f"""
                你是一个专业程序员。请生成以下单个文件的代码。

                ## 当前任务
                - 任务ID: {task['id']}
                - 目标语言: {task['language']}
                - 输出文件: {task['output_file']}
                - 任务描述: {task['description']}

                ## 你可以依赖的接口（已经生成好的）
                {dependency_context}

                ## 架构约束
                {constraints}

                ## 要求
                1. 只生成 {task['output_file']} 一个文件
                2. 代码完整，可直接运行
                3. 不要生成其他文件
                4. 只输出代码，不要解释

                ## 输出
                直接输出 {task['language']} 代码。
                """

def coding(requirement):
    CODING_PROMPT = f"""
    你是一个专业程序员。请根据以下用户需求生成完整可运行的代码。
    
    ## 用户需求：{requirement}
    
    ## 要求
    1.代码完整，可直接运行
    2.包含必要的注释
    3.遵循每种语言对于的规范

    ## 输出
    直接输出代码，不要用markdown代码块包裹。
    
    ## 约束：最小实现原则
    - 用最少的代码完成需求
    - 如果一行能解决，就只写一行
    - 不要为简单任务添加异常处理、函数封装、类型注解
    - 用户要的是可读性，不是防御性编程
    """
    result = ai.call(CODING_PROMPT)
    return result

def complexity_judge(requirement: str) -> str:
    if len(requirement) >= 30:
        hits = sum(1 for kw in COMPLEX_KEYWORDS if kw in requirement)
        if hits >= 2:
            return 'complex'
        elif hits == 1:
            return 'medium'
    return 'simple'

if __name__ == "__main__":
    if complexity_judge(REQUIREMENT) != 'simple':
        if complexity_judge(REQUIREMENT) == 'complex':
            ar = archi(2)
            st = structure(ar)
            ta = taskdispatch(st)
            coding = Dispatcher(ta, st)
        elif complexity_judge(REQUIREMENT) == 'medium':
            ar = archi()
            st = structure(ar)
            ta = taskdispatch(st)
            coding = Dispatcher(ta, st)
    re = coding(REQUIREMENT)
    print(re[1])

