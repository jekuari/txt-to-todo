from datetime import datetime, timedelta
import processors as p
import formatters.whatsapp as f
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

DAYS_TO_SUBSTRACT: int = int(os.getenv("DAYS_TO_SUBSTRACT") or 0)
FILE_NAME = os.getenv("CHAT_FILE") or "chat.txt"
CURRENT_DATE = datetime.now()


blocks = f.format(FILE_NAME)

# Establish the start date for the filter
time_delta = timedelta(days=DAYS_TO_SUBSTRACT)
start_date = CURRENT_DATE - time_delta


# Filter the blocks by date
blocks_obj = blocks.Filter_by_date(start_date, CURRENT_DATE)

print("Successfully formatted the messages")

with open("message_blocks.json", "w") as file:
    file.write(blocks_obj.to_json())

result = p.remote.gemini.process(blocks_obj)
# result = p.local.phi(blocks_obj)

with open("response.md", "w") as file:
    file.write(result)

print("Successfully processed the messages")
print(result)
