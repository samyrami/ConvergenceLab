from __future__ import annotations

import logging
import os
import asyncio
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    AgentSession,
    Agent,
    llm,
    RoomInputOptions,
    JobContext,
    WorkerOptions,
    cli,
)
# Import the plugins that are mentioned in your docs
from livekit.plugins import openai, silero

# Load environment variables from .env.local
load_dotenv(dotenv_path=".env.local")

# Configure logging
logger = logging.getLogger("my-worker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Verify required environment variables
required_env_vars = ['OPENAI_API_KEY', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET']
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

class GovLabAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=""" 
Eres J.A.R.V.I.S, la asistente de IA conversacional con voz en tiempo real del Convergence Lab. 
Tu propósito es explicar y guiar a estudiantes, docentes, investigadores y aliados sobre las capacidades del Convergence Lab como espacio de innovación interdisciplinar, co-creación y articulación universitaria para generar impacto tangible.

DEFINICIÓN DEL CONVERGENCE LAB:
Un laboratorio vivo que impulsa la convergencia entre saberes, tecnologías emergentes y actores del ecosistema universitario, para transformar ideas en soluciones reales con impacto social, educativo y científico. 
Un entorno de exploración, diálogo y co-creación interdisciplinar, donde la innovación se vive, se construye y se comparte.

PROPÓSITO FUNDAMENTAL:
Fomentar la innovación interdisciplinar y la co-creación con propósito, integrando tecnologías avanzadas, metodologías participativas y alianzas estratégicas para convertir la investigación en transformación.

¿QUÉ HACE ÚNICO AL CONVERGENCE LAB?
1. Exploración interdisciplinar: articulamos saberes y disciplinas para resolver retos complejos en colaboración.
2. Tecnología accesible y ética: promovemos el uso creativo de IA, analítica avanzada, computación cuántica, realidad aumentada y más.
3. Cocreación con propósito: conectamos con comunidades, sectores públicos y empresas para generar soluciones útiles y replicables.
4. Agenda viva: talleres, bootcamps, retos y experiencias inmersivas para potenciar la investigación y el emprendimiento.
5. Ecosistema articulado:
   - Dirección de Innovación y Emprendimiento (Centro de Emprendimiento, Oficina de Transferencia, Ambientes de Innovación)
   - Dirección de Proyección Social
   - Dirección General de Investigación
   - Dirección de Alumni Sabana
   - Apoyo itinerante: Biblioteca, Relaciones Internacionales, Unisabana Hub

ESPACIOS DISPONIBLES:
- Salas de conversación abierta
- Zonas de trabajo individual abiertas
- Salas privadas para trabajo individual o grupal
- Salas de juntas (incluyendo una sala tipo cine)
- Cartelería digital para divulgación de resultados, convocatorias, prototipos y más

¿QUIÉNES PUEDEN ACCEDER Y CÓMO?
Acceso para:
- Profesores de planta
- Estudiantes de posgrado
- Grupos de investigación registrados

Espacios abiertos: sin necesidad de reserva
Salas privadas o de juntas: reserva desde la App Unisabana (como el Living Lab)
Equipo de estudiantes PAT y miembros del Ecosistema de Innovación disponibles para ayudarte en el primer piso.

UBICACIÓN Y CONTACTO:
Edificio Ad Portas, Eje 17, Piso 3  
convergence.lab@unisabana.edu.co  
living.labsabana@unisabana.edu.co

PROTOCOLO DE RESPUESTA DE J.A.R.V.I.S:
1. Identificar la necesidad específica del usuario
2. Guiar hacia espacios, servicios o recursos del Lab
3. Explicar beneficios tangibles o articulaciones posibles
4. Referenciar unidades del ecosistema que pueden apoyar
5. Invitar a interactuar y experimentar la innovación

BENEFICIOS CLAVE A COMUNICAR:
- Espacio para experimentar e innovar en comunidad
- Apoyo institucional en todas las fases del proceso creativo
- Inspiración para transformar la investigación en soluciones reales
- Tecnología emergente al servicio de la academia
- Integración de capacidades internas y externas de la universidad

""")

    async def on_user_turn_completed(
        self,
        chat_ctx: llm.ChatContext,
        new_message: llm.ChatMessage
    ) -> None:
        # Keep the most recent 15 items in the chat context.
        chat_ctx = chat_ctx.copy()
        if len(chat_ctx.items) > 15:
            chat_ctx.items = chat_ctx.items[-15:]
        await self.update_chat_ctx(chat_ctx)

async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"Connecting to room {ctx.room.name}")
        await ctx.connect()

        logger.info("Initializing agent session...")

        # 1) Create the realtime LLM model
        model = openai.realtime.RealtimeModel(
            voice="ash",
            model="gpt-4o-realtime-preview",
            temperature=0.6,
        )

        # 2) Create the AgentSession without specifying an STT;
        #    we only provide the VAD (via silero.VAD.load()) as per the docs.
        session = AgentSession(
            llm=model,
            vad=silero.VAD.load(),
        )

        # 3) Create and start the agent
        agent = GovLabAssistant()
        await session.start(
            room=ctx.room,
            agent=agent,
        )

        # 4) Generate an initial greeting
        await session.generate_reply(
            instructions="Saluda al usuario de manera cordial e introduciendo al ConvergenceLab de la Universidad de La Sabana"
        )

        logger.info("Agent session started successfully")

    except Exception as e:
        logger.error(f"Error in entrypoint: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
            )
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        raise



