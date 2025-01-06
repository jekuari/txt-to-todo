import os
import google.generativeai as genai

def process(blocks_obj):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
    generation_config = genai.types.GenerationConfig(
      temperature= 1,
      top_p= 0.95,
      top_k= 40,
      max_output_tokens= 8192,
      response_mime_type= "text/plain",
    )

    file = open("agent_instructions/task_parser_gemini-flash.txt", "r")

    model = genai.GenerativeModel(
      model_name="gemini-2.0-flash-exp",
      generation_config=generation_config,
      system_instruction=file.read(),
    )

    file.close()


    def sendRequestToGemini(message: str):

        content = genai.types.ContentDict(role="user", parts=[message])

        chat_session = model.start_chat(
          history=[content]
        )

        response = chat_session.send_message("INSERT_INPUT_HERE")

        return response.parts[0].text

    return sendRequestToGemini(blocks_obj.to_json())
