# Text to todo list

## Why?
To be entirely honest this project was done by lazyness to keep track of the tasks my bosses assing to me via WhatsApp, I intend to add new chats in the future by changing the parsers.

## How?
What it basically does is take a certain amount of messages from the exported chat, and then uses ollama to ask the SLM's to process the messages and convert them into lists, which then get sent to another agent that cleans the tasks, removes unnecessary ones and add any missing details that can be inferred from the tasks.

## With?

It can basically use any LLM or SLM you tell it to use via the ollama.generate commands.

## Pre-requisites
- Python
- Conda

## Running it
- Specify the messages (Currently it only supports WhatsApp's exported txt files
- Load the conda environment from the yaml file
  ```bash
  conda env create -f environment.yml
  ```
- Activate it (Sorry I prefer conda than venv)
  ```bash
  conda activate txt-to-todo
  ```
- Install dependencies
  ```bash
  pip install -r requirements.txt
  ```
- Run the program
  ```bash
  python main.py
  ```
