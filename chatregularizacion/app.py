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
from utils.validators import check_email

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


@cl.on_chat_start
async def start():
    cl.user_session.set("agent_orchestrator", build_agent_orchestrator(SessionLocal))
    cl.user_session.set("chat_history", [])

    while cl.user_session.get("user_id") is None:
            res = await cl.AskUserMessage(
                content="Porfavor, introduce tu email para empezar la conversación", timeout=60
            ).send()
            if res:
                email = res["output"].strip()
                normalized_email = check_email(email)
                
                if normalized_email:
                    cl.user_session.set("user_email", normalized_email)
                    welcome_message = (
                        f"¡Hola, {normalized_email}!\n\n"
                        "Estoy aquí para acompañarte y resolver tus dudas basándome en el "
                        "**Manual sobre la Regularización Extraordinaria**. "
                        "Recuerda que esta información es **estrictamente orientativa y no tiene valor legal** "
                        "(el texto definitivo será el que se publique en el BOE).\n\n"
                        "¿En qué te puedo orientar hoy?"
                    )
                    await cl.Message(content=welcome_message).send()
                    return
                await cl.Message(content="Porfavor, escribe un email válido").send()


@cl.on_message
async def main(message: cl.Message):
    user_id = cl.user_session.get("user_email")
    if not user_id:
        await cl.Message(content="Session expired. Please restart.").send()
        return

    agent_orchestrator = cl.user_session.get("agent_orchestrator")
    chat_history = cl.user_session.get("chat_history", [])

    response, updated_history = await agent_orchestrator.process_message(
        message.content,
        user_id,
        chat_history,
    )
    cl.user_session.set("chat_history", updated_history)
    await cl.Message(content=response).send()
