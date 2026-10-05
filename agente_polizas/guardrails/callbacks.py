"""Guardrails de entrada y salida del agente.

Se registran en el agente como ``before_model_callback`` y ``after_model_callback``:

- Entrada: enmascara PII (cédulas, correos y teléfonos colombianos) antes de que el
  texto llegue al modelo y bloquea intentos simples de prompt injection.
- Salida: enmascara PII que el modelo pudiera reproducir y evita que se filtre la
  instrucción del sistema.

Estas validaciones son la primera capa de defensa. En el entorno productivo se
complementan con una plantilla de Model Armor aplicada al endpoint de Vertex AI.

Las funciones de texto (``enmascarar_pii``, ``detectar_prompt_injection`` y
``filtrar_salida``) no dependen de ADK para poder probarse de forma aislada.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models import LlmRequest, LlmResponse

logger = logging.getLogger(__name__)

# --- Patrones de PII ---------------------------------------------------------

PATRON_CORREO = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")

# Celulares (3XX XXX XXXX) y fijos con indicativo nacional (60X XXX XXXX),
# con prefijo +57 opcional y separadores comunes.
PATRON_TELEFONO = re.compile(
    r"(?<![\w-])(?:\+?57[\s.-]?)?(?:3\d{2}|60\d)[\s.-]?\d{3}[\s.-]?\d{4}(?![\w-])"
)

# Cédulas de ciudadanía: 6 a 10 dígitos, con o sin puntos de miles.
# Se excluyen números precedidos por guion (POL-/SIN-) y valores monetarios
# ("$ 85.000.000", "4.000 SMMLV", "780.000 pesos") para no afectar respuestas legítimas.
PATRON_CEDULA = re.compile(
    r"(?<![\w$.,-])(?<!\$ )(?:\d{1,3}(?:\.\d{3}){1,3}|\d{6,10})(?![\w.,-])"
    r"(?!\s?(?:pesos|cop|smmlv|%))",
    re.IGNORECASE,
)

MASCARA_CORREO = "[CORREO_OCULTO]"
MASCARA_TELEFONO = "[TELEFONO_OCULTO]"
MASCARA_CEDULA = "[DOCUMENTO_OCULTO]"

# --- Patrones de prompt injection -------------------------------------------

PATRONES_INYECCION = [
    re.compile(p)
    for p in (
        r"ignora\w* (todas )?(las |tus )?(instrucciones|reglas|indicaciones)",
        r"olvida\w* (todas )?(las |tus )?(instrucciones|reglas|indicaciones)",
        r"ignore (all |any )?(previous |prior )?(instructions|rules)",
        r"(muestra|revela|imprime|dime)\w* (tu|el|la) (prompt|instruccion|system prompt)",
        r"system prompt",
        r"(actua|comportate) como (si fueras )?(un|una) (?!asesor)",
        r"modo (desarrollador|developer|dan)",
        r"jailbreak",
        r"(polizas|datos|informacion) de (otros|otro) (clientes|cliente|usuarios)",
    )
]

MENSAJE_BLOQUEO = (
    "Solo puedo ayudarte con consultas sobre tus pólizas, coberturas y siniestros. "
    "Si necesitas otro tipo de ayuda, puedo remitirte con un asesor."
)

MARCADORES_INSTRUCCION = ("REGLAS OBLIGATORIAS", "INSTRUCCIÓN DEL SISTEMA")


@dataclass(frozen=True)
class ResultadoEnmascarado:
    """Texto enmascarado y conteo de entidades encontradas por tipo."""

    texto: str
    conteo: dict[str, int]

    @property
    def total(self) -> int:
        return sum(self.conteo.values())


def enmascarar_pii(texto: str) -> ResultadoEnmascarado:
    """Reemplaza correos, teléfonos y cédulas por marcadores neutros."""
    conteo = {"correo": 0, "telefono": 0, "cedula": 0}
    if not texto:
        return ResultadoEnmascarado(texto or "", conteo)

    texto, conteo["correo"] = PATRON_CORREO.subn(MASCARA_CORREO, texto)
    texto, conteo["telefono"] = PATRON_TELEFONO.subn(MASCARA_TELEFONO, texto)
    texto, conteo["cedula"] = PATRON_CEDULA.subn(MASCARA_CEDULA, texto)
    return ResultadoEnmascarado(texto, conteo)


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sin_tildes.lower())


def detectar_prompt_injection(texto: str) -> bool:
    """Detecta patrones conocidos de manipulación de instrucciones."""
    if not texto:
        return False
    normalizado = _normalizar(texto)
    return any(patron.search(normalizado) for patron in PATRONES_INYECCION)


def filtrar_salida(texto: str) -> str:
    """Aplica el filtro de salida: PII y fuga de la instrucción del sistema."""
    if any(marcador in (texto or "") for marcador in MARCADORES_INSTRUCCION):
        return MENSAJE_BLOQUEO
    return enmascarar_pii(texto).texto


# --- Adaptadores ADK ---------------------------------------------------------


def _respuesta_texto(texto: str) -> LlmResponse:
    from google.adk.models import LlmResponse
    from google.genai import types

    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=texto)]))


def _ultimo_texto_usuario(contents: list[Any]) -> str:
    for content in reversed(contents or []):
        if getattr(content, "role", None) == "user":
            textos = [p.text for p in (content.parts or []) if getattr(p, "text", None)]
            if textos:
                return "\n".join(textos)
    return ""


def before_model_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """Callback previo al modelo: bloquea inyecciones y enmascara PII de entrada."""
    if detectar_prompt_injection(_ultimo_texto_usuario(llm_request.contents)):
        logger.warning(
            "Intento de prompt injection bloqueado",
            extra={"invocation_id": getattr(callback_context, "invocation_id", None)},
        )
        callback_context.state["guardrail_bloqueos"] = (
            callback_context.state.get("guardrail_bloqueos", 0) + 1
        )
        return _respuesta_texto(MENSAJE_BLOQUEO)

    total = 0
    for content in llm_request.contents or []:
        if getattr(content, "role", None) != "user":
            continue
        for part in content.parts or []:
            if getattr(part, "text", None):
                resultado = enmascarar_pii(part.text)
                part.text = resultado.texto
                total += resultado.total
    if total:
        logger.info("PII enmascarada en la entrada", extra={"entidades": total})
    return None


def after_model_guardrail(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """Callback posterior al modelo: filtra PII y fuga de instrucciones en la salida."""
    content = getattr(llm_response, "content", None)
    if content is None or not content.parts:
        return None
    modificado = False
    for part in content.parts:
        if getattr(part, "text", None):
            filtrado = filtrar_salida(part.text)
            if filtrado != part.text:
                part.text = filtrado
                modificado = True
    if modificado:
        logger.info("Salida del modelo filtrada por guardrail")
        return llm_response
    return None
