# QueueFlow
Example of execution flow implementation using deque

You can extend with LLM by using LLFn [https://github.com/orgexyz/LLFn]


```

cd queueflow
poetry install
poetry run python main.py

```

## Example 

```
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
        out = self.DATA["input"]
        out = translate("HELLO, how are you ?","Thai")
        self.next(self.end, out)



if __name__ == "__main__":

    myflow = MyFlow1({"input" : "Hello, How are you ?"})
    myflow.run()
    
    out = myflow.output["result"]

    print(out)
```