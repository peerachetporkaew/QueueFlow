# QueueFlow
Example of execution flow implementation using deque

You can extend with LLM by using LLFn [https://github.com/orgexyz/LLFn]


python = 3.10 with poetry installed

```

cd queueflow
poetry install
poetry run python main.py

```

## Basic Example 

```python
from queueflow.queueflow import QueueFlow
from llfn import LLFn

function_prompt = LLFn()

@function_prompt
def translate(text: str, output_language: str) -> str:
    return f"Translate the following text into {output_language} language: {text}"

from langchain.chat_models import ChatOpenAI

# Setup LLM and bind it to the function
llm = ChatOpenAI(temperature=0.7, openai_api_key=os.getenv('OPENAI_API_KEY'))
translate.bind(llm)



class MyFlow1(QueueFlow):

    def __init__(self, datax={}):
        super().__init__("TEMP")
        self.DATA = datax


    def start(self):
        data = self.DATA["input"]
        out = translate(data)
        self.next(self.end, out)



if __name__ == "__main__":

    myflow = MyFlow1({"input" : "Hello, How are you ?"})
    myflow.run()
    
    out = myflow.output["result"]

    print(out)
```

## Advanced Example


This example shows the usage of the ``multiple_input_step`` decorator to hold execution until all inputs are ready.

```python
from queueflow.queueflow import QueueFlow, multiple_input_step
from llfn import LLFn

function_prompt = LLFn()

@function_prompt
def translate(text: str, output_language: str) -> str:
    return f"Translate the following text into {output_language} language: {text}"

from langchain.chat_models import ChatOpenAI

# Setup LLM and bind it to the function
llm = ChatOpenAI(temperature=0.7, openai_api_key=os.getenv('OPENAI_API_KEY'))
translate.bind(llm)


class MyFlow1(QueueFlow):

    def __init__(self, datax={}):
        super().__init__("TEMP")
        self.DATA = datax

    def start(self):
        out = self.DATA["input"]
        self.next(self.translate_to_thai, out)
        self.next(self.translate_to_chinese, out)

    def translate_to_thai(self,data):
        out = translate(data,"Thai")
        self.next(self.append, out) # This `out` is str.

    def translate_to_chinese(self,data): 
        out = translate(data,"Chinese")
        self.next(self.append, out) # This `out` is also str.


    @multiple_input_step(num_input=2)
    def append(self,data):
        out = " ||| ".join(data) # data now is a list of str.
        self.next(self.end, out)

if __name__ == "__main__":

    myflow = MyFlow1({"input" : "Hello, How are you ?"})
    myflow.run()
    
    out = myflow.output["result"]

    print(out) # สวัสดี คุณสบายดีไหม ? ||| 你好，你好吗？
```