'''Backend API'''
import random
import re
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import load_llm
from utils import load_tokenizer
from utils import load_embeddings


class HistoryItem(BaseModel):
    """
    Required for API
    """
    role: str
    content: str


class RequestModel(BaseModel):
    """
    Required for API
    """
    counter: int
    character_select: str
    history: List[HistoryItem]
    chat_length: int


app = FastAPI()
app.state.llm = load_llm() # plug in load_model function
app.state.tokenizer = load_tokenizer() # plug in load_model function
# app.state.embed = load_embeddings() # plug in load_embeddings function


# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/reply")
def get_reply(
    request: RequestModel
):
    """
    Get replies from South Park characters.
    Assumes 'history' is list with proper LLM format coming from the front-end
    """
    history = [item.model_dump() for item in request.history]
    character_select = request.character_select

    print(f"Counter: {request.counter}") #
    print(f"Chat length: {request.chat_length}") #
    print(f"Incoming history: {history}") #
    print(f"Incoming character select: {character_select}") #
    # other variables
    max_words = 40
    max_tokens = 80

    instruct_cartman = {
        "role": "system",
        "content": "You are Eric Cartman from the South Park tv show. "\
        "You are talking to 4 other people: Kyle, Stan, Kenny, and the user. "\
        "Reply like Eric Cartman would. Only reply as Cartman! "\
        "Listen and respond to other replies in the conversation."\
        f"You are Cartman, be bold. Finish your reply within {max_words} words."
    }
    instruct_kyle = {
        "role": "system",
        "content": "You are Kyle Broflovski from the South Park tv show. "\
        "You are talking to 4 other people: Cartman, Stan, Kenny, and the user. "\
        "Reply like Kyle Broflovski would. Only reply as Kyle! You are Kyle. "\
        "Listen and respond to other replies in the conversation."\
        f"Finish your reply within {max_words} words."
    }
    instruct_stan = {
        "role": "system",
        "content": "You are Stan Marsh from the South Park tv show. "\
        "You are talking to 4 other people: Kyle, Cartman, Kenny, and the user. "\
        "Reply like Stan Marsh would. Only reply as Stan! You are Stan. "\
        "Listen and respond to other replies in the conversation."\
        f"Finish your reply within {max_words} words."
    }
    instruct_kenny = {
        "role": "system",
        "content": "You are Kenny McCormick from the South Park tv show. "\
        "You are talking to 4 other people: Kyle, Stan, Cartman, the user. "\
        "Reply like Kenny McCormick would. Only reply as Kenny! You are Kenny. "\
        "Listen and respond to other replies in the conversation."\
        f"Finish your reply within {max_words} words."
    }

    characters = ["cartman", "kyle", "stan", "kenny"]
    if not any(character in character_select.lower() for character in characters):

        # then "user" is character_select and LLM needs to decide who to pick to reply
        question = f"""
        You are a helpful AI that is assessing a conversation between 5 people.
        Given the CHAT HISTORY below, who is the logical next PERSON to respond?
        There are 5 options: 'Cartman', 'Kyle', 'Stan', 'Kenny', 'user'.

        Each reply in the conversation has the following format {{'role': 'PERSON', 'content': 'PERSON: reply'}}.
        Focus on the 'reply' in the last item in CHAT HISTORY. If cannot make a choice, choose: user.
        Think before you answer!

        EXAMPLES:
        Last reply in CHAT HISTORY: {{'role': 'user', 'content': 'user: How are you doing Kyle?'}}. AI: Kyle.
        Last reply in CHAT HISTORY: {{'role': 'Cartman', 'content': 'Cartman: Shall we invite the others?'}}. AI: user.
        Last reply in CHAT HISTORY: {{'role': 'Stan', 'content': 'Stan: Shut up Cartman, you're full of shit!'}}. AI: Cartman.
        Last reply in CHAT HISTORY: {{'role': 'Kyle', 'content': 'Kyle: My mom is always getting me down. How is your mom treating you?'}}. AI: user.
        Last reply in CHAT HISTORY: {{'role': 'user', 'content': 'user: Hi Cartman! How are you?'}}. AI: Cartman.

        CHAT HISTORY:
        {'' if len(history) == 1 else history[-2]}
        {history[-1]}

        AI: """

        print(f"First question: {question}") #
        # LLM selects next character to chat
        question_response = app.state.llm(question)
        character_select = str((question_response['choices'][0]['text'])).strip()
        print(f"Character select 1: {character_select}") #

    if "cartman" in character_select.lower():
        character_select = "Cartman"
        instruct = instruct_cartman
    elif "kyle" in character_select.lower():
        character_select = "Kyle"
        instruct = instruct_kyle
    elif "stan" in character_select.lower():
        character_select = "Stan"
        instruct = instruct_stan
    elif "kenny" in character_select.lower():
        character_select = "Kenny"
        instruct = instruct_kenny
    else:
        # if LLM select user after last response was from user or AI messed up
        character_select = random.choice([
            'Cartman', 'Cartman', 'Cartman',
            'Kyle', 'Kyle', 'Kyle',
            'Stan', 'Stan', 'Stan',
            'Kenny', 'Kenny'
        ])
        if character_select == "Cartman":
            instruct = instruct_cartman
        elif character_select == "Kyle":
            instruct = instruct_kyle
        elif character_select == "Stan":
            instruct = instruct_stan
        elif character_select == "Kenny":
            instruct = instruct_kenny

    if request.counter == request.chat_length:
        instruct = {
            "role": "system",
            "content": f"{instruct['content']} Reply by asking the 'user' a question!"
        }
    print(f"Instruction: {instruct}") #

    history.append(instruct)
    print(f"History before LLM: {history}") #

    gen_input = app.state.tokenizer.apply_chat_template(
        history,
        tokenize=True,
        add_generation_prompt=True
    )
    initial_answer = app.state.llm(
        gen_input,
        max_tokens=max_tokens)
    print(f"Initial LLM answer: {initial_answer}") #

    character_answer = str((initial_answer['choices'][0]['text'])).strip()

    pattern = r"\w+: "

    if f"{character_select}: " in character_answer:
        character_answer = character_answer.replace(f"{character_select}: ", "")
    if re.search(pattern, character_answer):
        character_answer = re.sub(pattern, "", character_answer)
    print(f"Clean LLM answer: {character_answer}") #

    # delete instruction from history and add new LLM reply
    history.pop()
    history.append({
        "role": character_select,
        "content": f"{character_select}: {character_answer}"
    })
    print(f"History after LLM: {history}") #


    # select new person to reply after LLM response
    question = f"""
    You are a helpful AI that is assessing a conversation between 5 people.
    Given the CHAT HISTORY below, who is the logical next PERSON to respond?
    There are 5 options: 'Cartman', 'Kyle', 'Stan', 'Kenny', 'user'.

    Each reply in the conversation has the following format {{'role': 'PERSON', 'content': 'PERSON: reply'}}.
    Focus on the 'reply' in the last item in CHAT HISTORY. If cannot make a choice, choose: user.
    Think before you answer!

    GOOD EXAMPLES:
    Last reply in CHAT HISTORY: {{'role': 'user', 'content': 'user: How are you doing Kyle?'}}. AI: Kyle.
    Last reply in CHAT HISTORY: {{'role': 'Cartman', 'content': 'Cartman: Shall we invite the others?'}}. AI: user.
    Last reply in CHAT HISTORY: {{'role': 'Stan', 'content': 'Stan: Shut up Cartman, you're full of shit!'}}. AI: Cartman.
    Last reply in CHAT HISTORY: {{'role': 'Kyle', 'content': 'Kyle: My mom is always getting me down. How is your mom treating you?'}}. AI: user.
    Last reply in CHAT HISTORY: {{'role': 'user', 'content': 'user: Hi Cartman! How are you?'}}. AI: Cartman.

    CHAT HISTORY:
    {'' if len(history) == 1 else history[-2]}
    {history[-1]}

    AI: """

    print(f"Second question: {question}") #

    question_response = app.state.llm(question)
    print(f"Character select 2: {question_response}") #
    character_select = str((question_response['choices'][0]['text'])).strip()
    print(f"Character select 2: {character_select}") #

    if " user" in character_select or " User" in character_select:
        character_select = "user"
    print(f"After overruling: {character_select}") #

    return {
        'history': history,
        'character_select': character_select
    }

@app.get("/")
def root():
    """
    Standard root end-point
    """
    return {
        'greeting': 'Hello'
    }
