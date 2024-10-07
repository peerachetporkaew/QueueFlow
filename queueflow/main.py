import os
from langchain_core.globals import set_verbose, set_debug
# Disable verbose logging
set_verbose(False)
# Disable debug logging
set_debug(False)
import logging
logging.getLogger().setLevel(logging.ERROR)
import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")



from queueflow.queueflow import QueueFlow, multiple_inputs_step
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
        out = translate("HELLO, how are you ?","Thai")
        self.next(self.append, out)

    def translate_to_chinese(self,data):
        out = translate("HELLO, how are you ?","Chinese")
        self.next(self.append, out)


    @multiple_inputs_step(num_inputs=2)
    def append(self,data):
        out = " ||| ".join(data)
        self.next(self.end, out)

if __name__ == "__main__":

    myflow = MyFlow1({"input" : "Hello, How are you ?"})
    myflow.run()
    
    out = myflow.output["result"]

    print(out)
