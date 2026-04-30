import chainlit as cl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.repository.orm import start_mappers
from infrastructure.agent.agent_factory import build_agent_orchestrator
from config import (
    DATABASE_URI,
    ORM_CONNECTION_TIMEOUT,
    ORM_OVERFLOW_SIZE,
    ORM_POOL_SIZE,
)
import uuid

start_mappers()

engine = create_engine(
    DATABASE_URI,
    pool_size=ORM_POOL_SIZE,
    max_overflow=ORM_OVERFLOW_SIZE,
    pool_timeout=ORM_CONNECTION_TIMEOUT,
    connect_args={"sslmode": "allow"},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine)

EXAMPLE_QUESTIONS = [
    {
        "label": "¿Puedo acogerme?",
        "value": "¿Cuáles son los requisitos para poder acogerme a la regularización extraordinaria?",
        "name": "prompt_suggestion",
    },
    {
        "label": "¿Qué documentos necesito?",
        "value": "¿Qué documentación tengo que preparar para presentar la solicitud de regularización?",
        "name": "prompt_suggestion",
    },
    {
        "label": "¿Cómo demuestro mi estancia si no tengo padrón?",
        "value": "¿Cómo puedo demostrar que llevo al menos 5 meses viviendo en España si no tengo padrón?",
        "name": "prompt_suggestion",
    },
    {
        "label": "¿Cómo presento la solicitud?",
        "value": "¿Cómo y dónde puedo presentar la solicitud de regularización extraordinaria?",
        "name": "prompt_suggestion",
    },
    {
        "label": "¿Puedo trabajar al solicitarla?",
        "value": "¿Puedo empezar a trabajar legalmente desde que presento la solicitud o tengo que esperar a la resolución?",
        "name": "prompt_suggestion",
    },
    {
        "label": "¿Qué pasa después del primer año?",
        "value": "La autorización dura un año. ¿Qué tengo que hacer para renovarla o modificarla cuando se acabe?",
        "name": "prompt_suggestion",
    },
    {
        "label": "¿Qué es el informe de vulnerabilidad?",
        "value": "¿Qué es el certificado de vulnerabilidad, quién lo emite y cómo puedo conseguirlo?",
        "name": "prompt_suggestion",
    },
    {
        "label": "¿Qué son las entidades colaboradoras?",
        "value": "¿Qué son las entidades colaboradoras con Extranjería, cómo pueden ayudarme con mi solicitud y donde las puedo encontrar?",
        "name": "prompt_suggestion",
    },
    {
        "label": "Tengo asilo, ¿puedo acogerme?",
        "value": "Soy solicitante de protección internacional (asilo). ¿Puedo acogerme a la regularización extraordinaria sin renunciar a mi solicitud de asilo?",
        "name": "prompt_suggestion",
    },
    {
        "label": "¿Dónde consulto más información?",
        "value": "¿Dónde puedo encontrar los formularios oficiales, enlaces y teléfonos de contacto para la regularización extraordinaria?",
        "name": "prompt_suggestion",
    },
]



async def _process_message(content: str):
    """Shared logic: sends user content to the agent orchestrator and replies."""
    user_id = cl.user_session.get("user_id")
    if not user_id:
        await cl.Message(content="Session expired. Please restart.").send()
        return

    agent_orchestrator = cl.user_session.get("agent_orchestrator")
    chat_history = cl.user_session.get("chat_history", [])

    response, updated_history = await agent_orchestrator.process_message(
        content,
        user_id,
        chat_history,
    )
    cl.user_session.set("chat_history", updated_history)
    await cl.Message(content=response).send()


@cl.on_chat_start
async def start():
    cl.user_session.set("agent_orchestrator", build_agent_orchestrator(SessionLocal))
    cl.user_session.set("chat_history", [])
    cl.user_session.set("user_id", str(uuid.uuid4()))

    welcome_message = (
        "¡Hola!\n\n"
        "Estoy aquí para acompañarte y resolver tus dudas basándome en el "
        "**Manual sobre la Regularización Extraordinaria**. "
        "Recuerda que esta información es **estrictamente orientativa y no tiene valor legal**.\n\n"
        "¿En qué te puedo orientar hoy?"
    )

    actions = [
        cl.Action(name=q["name"], payload={"value": q["value"]}, label=q["label"])
        for q in EXAMPLE_QUESTIONS
    ]

    await cl.Message(content=welcome_message, actions=actions).send()


@cl.action_callback("prompt_suggestion")
async def on_action(action: cl.Action):
    user_question = action.payload.get("value")
    await cl.Message(content=user_question, type="user_message").send()
    await _process_message(user_question)


@cl.on_message
async def main(message: cl.Message):
    await _process_message(message.content)
