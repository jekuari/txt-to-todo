import ollama
import models as m

def process(blocks_obj):
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
        blocks_to_process = blocks_obj.blocks[i:i+5]
        blocks_section = m.MessageBlocks(blocks_to_process)
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


    Reasoning Behind The Output (Not to be included in the response):
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

    return completeResponse
