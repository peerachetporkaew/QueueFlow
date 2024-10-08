
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



from queueflow.queueflow import QueueFlow, multiple_input_step

from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

from llfn import LLFn

function_prompt = LLFn()

@function_prompt
def translate(text: str, output_language: str) -> str:
    return f"Translate the following text into {output_language} language: {text}"

from langchain.chat_models import ChatOpenAI

# Setup LLM and bind it to the function
llm = ChatOpenAI(temperature=0.7, openai_api_key=os.getenv('OPENAI_API_KEY'))
translate.bind(llm)

import instructor

class Character(BaseModel):
    name: str
    age: int
    fact: List[str] = Field(..., description="A list of facts about the character")


# enables `response_model` in create call
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    ),
    mode=instructor.Mode.JSON,
)


def get_character_details(name):
    resp = client.chat.completions.create(
        model="gemma:2b",
        messages=[
            {
                "role": "user",
                "content": f"Tell me about {name}",
            }
        ],
        response_model=Character,
    )
    return resp

#out = get_character_details("Tom Hank")
#print(out)

def translatetemp(data,lang):
    return lang + " :: " + data


class MyFlow1(QueueFlow):

    def __init__(self, datax={}):
        super().__init__("TEMP")
        self.DATA = datax

    def start(self):
        out = self.DATA["input"]
        self.next(self.get_character_details, out)
        

    def get_character_details(self,data):
        print("STEP :: Get Charater Details")
        out = get_character_details(data)
        print("OUT :: ", out)
        self.next(self.translate_to_chinese, out.name)
        self.next(self.translate_to_chinese, out.fact)
        self.next(self.merge, {"age" : out.age})


    def translate_to_chinese(self,data):
        print("STEP :: Translate to Chinese", data)
        if isinstance(data,str):
            out = { "name" : translate(data,"Chinese") }
            
        elif isinstance(data,list):
            temp = {"fact" : []}
            for item in data:
                temp["fact"].append(translate(item,"Chinese"))
            out = temp

        self.next(self.merge, out)


    @multiple_input_step(num_input=3)
    def merge(self,data):
        print("STEP :: MERGE")
        out = data[0]
        out.update(data[1])
        out.update(data[2])
        self.next(self.end, out)

if __name__ == "__main__":

    myflow = MyFlow1({"input" : "Tom Hank"})
    myflow.run()
    out = myflow.output["result"]
    print(out)
