from datetime import datetime, timedelta
import json
import ollama
import re

END_CHAR = """"""
USER_NAME = "Ricardo F."

def convert_to_iso_and_datetime(date_string):
  """
  Converts a date string with the format 'MM/DD/YY, HH:MM:SS p.m.' to 
  an ISO-formatted date string (RFC3339) and then to a datetime object.

  Args:
    date_string: The date string to convert.

  Returns:
    A datetime object representing the input date and time.
  """
  try:
    # Split the string into date and time parts
    date_part, time_part = date_string.split(', ')

    # Split date and time components
    day, month, year = date_part.split('/')
    hour, minute, second = time_part.split(':')[:3]  # Ignore AM/PM for now

    # Get AM/PM indicator
    am_pm = time_part.split()[-1].lower()
    second = second.split()[0].lower()

    # Adjust hour for 24-hour format
    if am_pm == 'p.m.' and hour != '12':
      hour = str(int(hour) + 12)
    elif am_pm == 'a.m.' and hour == '12':
      hour = '00'

    def add_zero(num):
        return str(num) if len(str(num)) == 2 else '0' + str(num)

    # Construct ISO-formatted string (YYYY-MM-DDTHH:MM:SS)
    iso_date_string = f"20{year}-{add_zero(month)}-{add_zero(day)}T{add_zero(hour)}:{add_zero(minute)}:{add_zero(second)}"

    # Convert to datetime object
    datetime_object = datetime.fromisoformat(iso_date_string)

    return datetime_object

  except ValueError:
    return None

class Message:
    content: str = ""
    date: datetime = datetime.now()
    user: str = ""


    def __init__(self, content: str, date: datetime, user: str):
        self.content = content
        self.date = date
        self.user = user

    def __str__(self) -> str:
        return "{\n"+ f"\"date\": \"{self.date}\",\n\"user\":\"{self.user}\",\n\"message\":\"{self.content}\"\n" + "}"

    def to_llm_readable(self) -> str:
        obj = {
            "sender": "Me" if self.user == USER_NAME else "Boss",
            "timestamp": str(self.date),
            "message": self.content
        }

        return json.dumps(obj)

    def to_obj(self):
        return {
            "message": self.content,
            "timestamp": str(self.date),
            "sender": "Me" if self.user == USER_NAME else "Boss"
        }

class MessageBlocks:
    blocks: list[Message] = []

    def __init__(self, blocks: list[Message]):
        self.blocks = blocks

    def __str__(self):
        return ",\n".join([str(block) for block in self.blocks])
    
    def to_llm_readable(self) -> str:
        return "\n".join([block.to_llm_readable() for block in self.blocks])

    def to_json(self) -> str:
        return json.dumps([block.to_obj() for block in self.blocks], ensure_ascii=False)

    def Filter_by_date(self, start_date: datetime, end_date: datetime):
        return MessageBlocks([block for block in self.blocks if start_date <= block.date <= end_date])

    def filter_by_date(self, start_date: datetime, end_date: datetime):
        self.blocks = [block for block in self.blocks if start_date <= block.date <= end_date]

blocks: list[Message] = []

date_regex = r"\[(.*)\]"
dr = re.compile(date_regex)

# user has the format, and is located just next to the closing bracket ' Boss: '
userRegex = r"\ (.*):\ "
ur = re.compile(userRegex)


with open("alex_chat.txt", "r") as file:
    content = ""
    date = ""
    user = ""
    for line in file:
        if "omitted" in line and line[-1] == END_CHAR:
            continue

        if "[" in line:
            content = ""
            original_line = line
            opening_bracket_index = line.find("[")
            closing_bracket_index = line.find("]")

            in_brackets = line[opening_bracket_index + 1:closing_bracket_index ]
            # date comes in format 24/12/24, 9:08:25 p.m., we need to convert that into a datetime object
            
            normalized_date_string = in_brackets.replace("\u202F", " ")

            iso_date_string = convert_to_iso_and_datetime(normalized_date_string)
            if iso_date_string is None:
                continue

            date = iso_date_string

            line = line[closing_bracket_index + 1:]
            two_points_index = line.find(":")

            user = line[:two_points_index].strip()

            line = line[two_points_index + 2:]

            if original_line[-1] == END_CHAR:
                content += line.replace("\n", "")
                blocks.append(Message(content, date, user))
                continue
            else:
                content += line
        elif line[-1] == END_CHAR:
            content += line.replace("\n", "")
            blocks.append(Message(content, date, user))
        else:
            content += line


# filter by date, the date has the format: [21/07/24, 3:10:31 p.m.]
CURRENT_DATE = datetime.now()
# minus one month

# Number of days to subtract
days_to_subtract = 4

# Create a timedelta object representing the number of days
time_delta = timedelta(days=days_to_subtract)

# Subtract the timedelta from the date
start_date = CURRENT_DATE - time_delta

blocks_obj = MessageBlocks(blocks)
blocks_obj = blocks_obj.Filter_by_date(start_date, CURRENT_DATE)

print("Approximate tokens:", len(str(blocks_obj)) / 4)

with open("message_blocks.json", "w") as file:
    file.write(blocks_obj.to_json())

# with open("./Modelfile") as f:
#     modelfile = f.read()
#     ollama.create(model='taskparser', modelfile=modelfile)
#
# print("Updated model")

modelfile = """
Instruction: You are a task extraction assistant. Your goal is to analyze chat messages between boss and myself (me). Identify messages from boss that assign tasks to me. For each identified task assignment, extract the task and represent it in a structured format, including the timestamp of the message where the task was identified.

Context:
- The chat is in Spanish.
- Tasks can be directives or requests from boss to me to perform some action.
- Tasks can be simple or complex, and they might be spread across multiple messages.
- Tasks should be extracted in Spanish.
- Tasks should be marked as incomplete.

Input Data Format:
The chat history will be provided as a list of messages. Each message will be a JSON object with the following structure:

{
  "sender": "Boss" or "Me",
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "message": "The text content of the message in Spanish"
}

Output Data Format:
Your response should be a list of tasks. Each task should be on a new line.

- [] YYYY-MM-DD HH:MM:SS | Task description in Spanish

Example of a full interaction:
[
  {
    "sender": "Boss",
    "timestamp": "2024-07-27 10:00:00",
    "message": "Hola! Necesito que revises el documento de diseño."
  },
  {
    "sender": "Me",
    "timestamp": "2024-07-27 10:05:00",
    "message": "Ok, lo haré."
  }
]

Output:
- [] 2024-07-27 10:00:00 | Revisar documento. 

Additional Notes:
- Focus on identifying tasks within the chat history.
- Pay special attention to messages that describe bugs or errors. Convert these into actionable tasks for fixing the issues.
- If no tasks are found, ignore the message, don't mention them.
- Maintain the original Spanish phrasing in the extracted tasks.
- The timestamp provided in the input is for context. Use it to prefix each extracted task in the output, allowing the user to search for the original message based on the task.
- **Be concise in your response. Avoid unnecessary explanations or elaborations.** 
- Convert any escaped characters to their unescaped form eg. "\u00ed" to "í".
- Only messages from boss are possible tasks.
- Not all groups of messages will contain tasks, it's not necessary to extract tasks from all messages.
"""

combined_responses = []
# considering that the model is small, only process 5 messages at a time
for i in range(0, len(blocks_obj.blocks), 5):
    print(f"Processing blocks {i} to {i+5} out of {len(blocks_obj.blocks)} {i/len(blocks_obj.blocks) * 100}%")
    blocks_to_process = blocks_obj.blocks[i:i+5]
    blocks_section = MessageBlocks(blocks_to_process)
    res = ollama.generate(
        model = "phi3.5:latest",
        system = modelfile,
        prompt = blocks_section.to_json(),
        stream = True
    )

    completeResponse = ""
    for chunk in res:
        completeResponse += chunk.response
    
    combined_responses.append(completeResponse)

raw_tasks = "\n".join(combined_responses)

print("Finished processing all blocks, starting post-processing...")
# Post-process the responses to make them more readable and concise
post_processing_instruction = """
Instruction: You are a task consolidation and refinement agent. You will receive a list of extracted tasks from various segments of a chat conversation. Your job is to analyze these tasks, refine them, and present a coherent and concise set of tasks.

Input Data Format:
The input will be a list of tasks, each with a timestamp and description:

- [] YYYY-MM-DD HH:MM:SS | Task description in Spanish

Example Input:
- [] 2025-01-02 14:15:08 | Dejar los documentos para revisión mañana.
- [] 2025-01-02 14:15:14 | Comunicar dudas sobre el trabajo realizado en relación a los documentos.
- [] 2024-12-31 19:36:38 | Recibir el paquete para el jueves.
- [] 2025-01-02 10:06:03 | Retomar todo proyecto.
- [] 2025-01-02 10:06:23 | Hacer en tiempo y forma para recibir dinero.
- [] 2025-01-02 10:06:35 | Junta lo que falta ahorita.
- [] 2025-01-02 12:56:53 | Configurar las constantes del proyecto.
- [] 2025-01-02 14:15:08 | Dejar los documentos para revisión mañana.
- [] 2025-01-02 14:15:14 | Comunicar dudas sobre el trabajo realizado en relación a los documentos.


Output Data Format:
Your response should be a refined and organized list of tasks in the SAME format as the input, potentially grouped by timestamps, and free of redundancies.

Example Output:
- [] 2025-01-02 12:56:53 | Configurar las constantes del proyecto.
- [] 2025-01-02 10:06:03 | Retomar el proyecto, completarlo en tiempo y forma para recibir el pago. (This combines and rephrases related tasks for clarity)
- [] 2025-01-02 10:06:35 | Juntar lo que falta en el proyecto. 
- [] 2025-01-02 14:15:08 | Dejar los documentos para revisión mañana y comunicar cualquier duda sobre el trabajo realizado. (This combines related tasks)
- [] 2024-12-31 19:36:38 | Recibir el paquete para el jueves.

Reasoning Behind The Output:
- The word "constantes" suggests a programming project.
- Tasks related to the project are grouped together by their timestamps.
- Redundant tasks are removed.
- The output is organized and easy to understand.

Additional Notes:
- Analyze the tasks for clues about the context or nature of the work.
- Remove any unnecessary notes or comments that are not actual tasks.
- Group related tasks together and rephrase them for clarity and conciseness.
- Present the output in a clear and organized manner, using the same format as the input.
- Ensure that the output is free of reasoning or explanations, focusing solely on the refined tasks.
- If something is not a task, ignore it. We area only interested in actionable items.
"""

res = ollama.generate(
    model = "phi3.5:latest",
    system = post_processing_instruction,
    prompt = raw_tasks,
    stream = True
)

completeResponse = ""
for chunk in res:
    completeResponse += chunk.response

print(f"Your tasks are:\n{completeResponse}")
