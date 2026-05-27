import asyncio
from api.routes import chat, ChatRequest
from agents.state import DermaFlowState
from agents.orchestrator import app
import base64

request = ChatRequest(
    query="hello",
)

try:
    asyncio.run(chat(request))
except Exception as e:
    import traceback
    traceback.print_exc()
