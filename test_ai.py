import asyncio
import os
import json
from dotenv import load_dotenv
load_dotenv()
from app.ai_modules import _configure_client
import google.generativeai as genai
import logging
logging.basicConfig(level=logging.ERROR)
async def test():
    _configure_client()
    models = [m.name for m in genai.list_models()]
    with open("models.json", "w") as f:
        json.dump(models, f)

if __name__ == "__main__":
    asyncio.run(test())
