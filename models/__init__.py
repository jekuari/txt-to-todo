from datetime import datetime, timedelta
import json
import constants as c

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
            "sender": "Me" if self.user == c.USER_NAME else "Boss",
            "timestamp": str(self.date),
            "message": self.content
        }

        return json.dumps(obj)

    def to_obj(self):
        return {
            "message": self.content,
            "timestamp": str(self.date),
            "sender": "Me" if self.user == c.USER_NAME else "Boss"
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
