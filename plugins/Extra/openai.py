# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging

try:
    import openai
except ImportError:
    openai = None

async def ai(query):
    if not openai:
        return "OpenAI library is not installed."
    try:
        # OpenAI API Handler
        response = await openai.Completion.acreate(
            engine="text-davinci-002",
            prompt=query,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.9
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"OpenAI Error: {e}"
     
async def ask_ai(client, m, message):
    try:
        if len(message.text.split(" ", 1)) < 2:
            return await m.edit("Please provide a query.")
        question = message.text.split(" ", 1)[1]
        response = await ai(question)
        await m.edit(f"{response}")
    except Exception as e:
        await m.edit(f"An error occurred: {e}")
