import re
from datetime import datetime
import models as m
import constants as c
from formatters.utils.whatsapp_date_to_datetime import convert_to_iso_and_datetime

def format(path: str) -> m.MessageBlocks:
    blocks: list[m.Message] = []

    date_regex = r"\[(.*)\]"
    dr = re.compile(date_regex)

# user has the format, and is located just next to the closing bracket ' Boss: '
    userRegex = r"\ (.*):\ "
    ur = re.compile(userRegex)


    with open(path, "r") as file:
        content = ""
        date = datetime.now()
        user = ""
        for line in file:
            if "omitted" in line and line[-1] == c.END_CHAR:
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

                if original_line[-1] == c.END_CHAR:
                    content += line.replace("\n", "")
                    blocks.append(m.Message(content, date, user))
                    continue
                else:
                    content += line
            elif line[-1] == c.END_CHAR:
                content += line.replace("\n", "")
                blocks.append(m.Message(content, date, user))
            else:
                content += line

    return m.MessageBlocks(blocks)
