"""
Description: LUNA主程序。
"""
from model import deepseek, llama
import asyncio
from collections import deque
from pathlib import Path
from time import time, localtime
from Luna.DataBase.lunadb import LunaDB
from colorama import init, Fore
import json


init()
db = LunaDB()
ai = deepseek.Use(name="archi", base_url="", api_key="")
lama = llama.Use(name="llama", base_url="", api_key="")
COMPLEX_KEYWORDS = [
    '系统', '平台', '多个模块', '前后端', '数据库',
    '登录', '权限', '部署', '微服务', 'API', '管理后台'
]
REQUIREMENT = input('>>> ')
start = time()

LANGUAGE_EXT = {
    "python": ".py",
    "javascript": ".js",
    "css": ".css",
    "html": ".html",
    "c++": ".cpp",
    "c": ".c",
    "go": ".go",
    "rust": ".rs",
    "java": ".java",
}

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
      "location": "属于架构当中的哪个模块",
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
      "location": "属于架构当中的哪个模块",
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
        result = ai.call(ARCHI_PROMPT+EXTRA_ARCHI_PROMPT, int(time() - start))
    else:
        result = ai.call(ARCHI_PROMPT, int(time() - start))
    print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成结构设计 (Duration Time {int(time() - start)})')
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
    result = ai.call(STRUCTURE_PROMPT, int(time() - start))
    print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成架构分析 (Duration Time {int(time() - start)})')
    return result

def taskdispatch(structure_result):
    TASKS_PROMPT = f"""
    你是一个任务规划专家。请将以下架构方案拆分为可执行的子任务。不要用markdown格式。
    不要有任何解释。只输出json。

    ## 架构方案：{structure_result}

    ## 任务列表：
    1. 拆分子任务，粒度适中 (每个任务一个文件或一个模块)
    2. 标注任务间依赖关系
    3. 为每个任务定义输入输出接口
    4. 输出依赖图

    ## 输出格式：{TASKS_STRUCTURE}
    
    只输出JSON，不要输出任何解释、前言或总结。
    """
    result = ai.call(TASKS_PROMPT, int(time() - start))
    print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成任务拆分 (Duration Time {int(time() - start)})')
    return result

def save_code_file(filename: str, language: str, code: str):
    ext = LANGUAGE_EXT.get(language.lower(), ".txt")
    full_path = Path(filename)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(code, encoding="utf-8")
    return full_path

class Dispatcher:
    def __init__(self, tsk, stru: dict):
        self.tsk = json.loads(tsk)
        self.stru = stru
        self.unfinished = []
        self.finished = []
        self.interface = []
        self.dq_unf = deque(self.unfinished)
        self.dq_f = deque(self.finished)
        self.dq_inter = deque(self.interface)

    def add_finished_task(self, finished_task):
        self.dq_f.append(finished_task)

    def execution(self, t):
        inter = ''
        for i in self.interface:
            inter += f'{i}, '

        CODING_PROMPT = f"""
        你是一个资深软件工程师。你正在参与一个复杂项目的开发。

        ## 完整项目架构（必须严格遵守）
        {self.stru}

        ## 当前需要你完成的任务
        - 任务 ID：{t["id"]}
        - 目标语言：{t["language"]}
        - 输出文件：{t["output_file"]}
        - 任务描述：{t["description"]}

        ## 该任务在架构中的位置
        - 所属模块：{t["location"]}
        
        ## 已有依赖接口（已生成好的）
        {inter}

        ## 你的职责边界
        1. 只生成 {t["language"]} 这一个文件
        2. 只实现当前任务描述中要求的功能
        3. 不要越界实现其他模块的职责
        4. 不要修改架构设计
        5. 所有对外接口必须与架构文档一致

        ## 编码规范
        1. 遵循 {t["language"]} 标准编码规范
        2. 完整的导入、错误处理、类型标注
        3. 不写 TODO、pass 或占位符
        4. 代码可直接运行

        ## 输出要求
        只输出 {t["language"]} 代码本身。
        不要输出 markdown 代码块。
        不要解释。
        不要写"以下是代码"。
        """

        code = ai.call(CODING_PROMPT, int(time() - start), retries=3)
        print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成{t["id"]}任务的代码生成 (Duration Time {int(time() - start)})')
        path = save_code_file(t["output_file"], t["language"], code[0][0][1])
        print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已保存{t["id"]}任务的代码到{str(path)} (Duration Time {int(time() - start)})')
        self.dq_inter.append(t["interface"]["provides"])
        self.add_finished_task(t["id"])

    def task_dispatch(self):
        print(f'tasks len: {len(self.tsk["Tasks"])}')
        for t in self.tsk["Tasks"]:
            self.unfinished.append(t["id"])
            if len(self.unfinished) == len(self.tsk["Tasks"]):
                break
        while self.unfinished:
            for tk in self.tsk["Tasks"]:
                print(f'Depends: {tk["depend"]}')
                if not tk["depend"] or tk["depend"] in self.finished:
                    if tk["id"] not in self.finished:
                        print(f'Executing task: {tk["id"]}...')
                        self.execution(tk)
                        self.finished.append(tk["id"])
                        self.unfinished.remove(tk["id"])
                        print(f'finished list: {self.finished}')
                        print(f'unfinished list: {self.unfinished}')
        return 1

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
    print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成prompt组装，正在进行call函数调用 (Duration Time {int(time() - start)})')
    result = ai.call(CODING_PROMPT, int(time() - start))
    print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成call调用，正在返回结果 (Duration Time {int(time() - start)})')
    return result

def complexity_judge(requirement: str) -> str:
    JUDGE_PROMPT = f"""
    判断以下用户需求的复杂度。只输出 simple、medium 或 complex 三个词之一，不要解释。
    
    ## 判断标准

    simple（简单）：
    - 单文件、少量代码（<30行）
    - 无外部依赖或仅标准库
    - 一次性执行，无持续运行
    - 输入输出明确，无交互逻辑

    medium（中等）：
    - 涉及外部库
    - 需要持续运行或监听
    - 有交互逻辑（用户输入、按键、事件）
    - 需要错误处理或退出机制
    - 多步骤流程

    complex（复杂）：
    - 多文件、多模块
    - 涉及数据库、网络、前后端
    - 需要架构设计
    - 多Agent协作
    
    ## 用户需求：{requirement}
    
    ## 输出
    只输出：simple / medium / complex，不要任何标点、空格、解释、引号。
    """
    print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 正在调用llama进行复杂度判断 (Duration Time {int(time() - start)})')
    result = lama.call(JUDGE_PROMPT, int(time() - start), retries=3)
    print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} llama已返回数据 (Duration Time {int(time() - start)})')
    return result

def write_in(content) -> None:
    with open('D:/Lunarez/Lunarez.LUNA/Luna/model/outputs/ds.txt', 'a', encoding='utf-8') as f:
        f.write(f'{f'User request: {REQUIREMENT}\n'+f'Time:{localtime()}\n'+content}\n\n')

if __name__ == "__main__":
    COMPLEXITY = complexity_judge(REQUIREMENT)
    if COMPLEXITY:
        COMPLEXITY = COMPLEXITY[0][0].strip().lower()
        if COMPLEXITY == 'complex':
            print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成复杂度判断 ({Fore.RED}complex{Fore.RESET}) (Duration Time {int(time() - start)})')
            ar = archi(2)
            st = structure(ar[0][0][1])
            ta = taskdispatch(st[0][0][1])
            coding = Dispatcher(ta[0][0][1], st[0][0][1])
            re = coding.task_dispatch()
        elif COMPLEXITY == 'medium':
            print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成复杂度判断 ({Fore.YELLOW}medium{Fore.RESET}) (Duration Time {int(time() - start)})')
            ar = archi()
            st = structure(ar[0][0][1])
            ta = taskdispatch(st[0][0][1])
            coding = Dispatcher(ta[0][0][1], st[0][0][1])
            re = coding.task_dispatch()
        elif COMPLEXITY == 'simple':
            print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成复杂度判断 ({Fore.GREEN}simple{Fore.RESET})，正在调用coding函数 (Duration Time {int(time() - start)})')
            re = coding(REQUIREMENT)
        else:
            print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 复杂度判断异常，自动归类为 {Fore.YELLOW}medium{Fore.RESET} (Duration Time {int(time() - start)})')
            ar = archi()
            st = structure(ar[0][0][1])
            ta = taskdispatch(st[0][0][1])
            coding = Dispatcher(ta[0][0][1], st[0][0][1])
            re = coding.task_dispatch()
    else:
        print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 复杂度判断异常，自动归类为 {Fore.YELLOW}medium{Fore.RESET} (Duration Time {int(time() - start)})')
        ar = archi()
        st = structure(ar[0][0][1])
        ta = taskdispatch(st[0][0][1])
        coding = Dispatcher(ta[0][0][1], st[0][0][1])
        re = coding.task_dispatch()

    print('\n' + Fore.RED + '===== LUNA OUTPUT =====' + '\n' +
          Fore.RESET + re[0][0][1] + '\n' +
          Fore.RED + '=======================' + '\n')

    if db.inputdb(REQUIREMENT, int(time()-start), re[0][0][1]):
        print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已存入数据库')

    write_in(re[0][0][1])
    print(f'{Fore.WHITE}[CONSOLE]{Fore.RESET} 已完成请求 (Duration Time: {int(time()-start)})')


