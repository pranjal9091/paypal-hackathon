import re
from typing import Dict, Any, Optional
from app.llm_client import llm_client

DEFAULT_LANDING_PAGE_MARKDOWN = """# TidyLedger — La Contabilidad Inteligente para Startups y Pymes

## El Problema
Gestionar las finanzas de un negocio emergente suele convertirse en una pesadilla de hojas de cálculo desordenadas, facturas extraviadas y horas perdidas en tareas manuales. Los emprendedores pierden tiempo valioso cuadrando números en lugar de hacer crecer su producto.

## La Solución
TidyLedger centraliza, automatiza y simplifica toda la contabilidad de tu empresa en una única plataforma en la nube. Desde la emisión de facturas electrónicas hasta la conciliación bancaria instantánea, te ayudamos a mantener tus finanzas transparentes y al día con un esfuerzo mínimo.

## Características Principales
- **Facturación Automatizada:** Crea y envía facturas profesionales personalizadas en segundos con cálculo automático de impuestos.
- **Conciliación Bancaria en Tiempo Real:** Conecta tus cuentas y sincroniza transacciones de forma segura y sin duplicados.
- **Reportes Financieros Claros:** Visualiza tu flujo de caja, balance general y estado de resultados mediante gráficos comprensibles.
- **Colaboración Segura:** Comparte acceso controlado con tu contador y equipo administrativo sin exponer credenciales bancarias.

## Llamado a la Acción
Comienza hoy mismo a tomar el control total de las finanzas de tu negocio. Regístrate ahora y disfruta de 14 días de prueba gratuita sin compromiso.
"""

class ContentAgent:
    """
    Specialist Agent 2: Content Agent.
    Produces landing_page_es.md from the approved contract brief.
    Mandatory Rules:
    - Follows explicit Markdown structure (H1 Title + 4 required H2 sections).
    - Strict word count constraints (150 - 450 words).
    - No unsupported claims (no fake banking claims or guaranteed returns).
    """

    @classmethod
    async def execute(
        cls,
        contract_title: str,
        contract_desc: str,
        simulate_missing_section: bool = False,
        simulate_word_count_violation: bool = False,
        simulate_unsupported_claim: bool = False,
        force_fallback: bool = False
    ) -> Dict[str, Any]:
        # Demo / Test failure scenario hooks
        if simulate_word_count_violation:
            # Bare 15-word stub
            return {
                "filename": "landing_page_es.md",
                "content": "# TidyLedger\n\nTexto demasiado corto para una página de aterrizaje profesional.",
                "is_fallback": True,
                "provider": "simulated-word-count-failure",
                "mode": "fallback"
            }

        fallback = DEFAULT_LANDING_PAGE_MARKDOWN.strip()

        if simulate_missing_section:
            # Strip the CTA section to trigger deterministic section check failure
            fallback = re.sub(r"## Llamado a la Acción[\s\S]*$", "", fallback).strip()

        if simulate_unsupported_claim:
            fallback += "\n\nNota: Somos un banco autorizado con garantía de 100% rentabilidad financiera garantizada por ley."

        system_instruction = (
            "You are a professional conversion copywriter specializing in Spanish SaaS landing pages. "
            "Write high-converting, professional landing page copy in Markdown for the product described. "
            "You MUST use this EXACT section structure:\n"
            "# <Product Title>\n"
            "## El Problema\n"
            "## La Solución\n"
            "## Características Principales\n"
            "## Llamado a la Acción\n"
            "Keep total length between 180 and 380 words. Do NOT invent fake financial licenses or guarantees."
        )
        prompt = (
            f"Generate a Spanish landing page for:\nProduct: {contract_title}\nBrief: {contract_desc}"
        )

        llm_res = await llm_client.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            fallback_content=fallback,
            force_fallback=force_fallback
        )

        content = llm_res.content
        # Basic validation: if live output lacks H1 title, fall back to robust baseline
        if not llm_res.is_fallback:
            if not content.startswith("# ") or "## El Problema" not in content:
                content = fallback
                llm_res.is_fallback = True
                llm_res.mode = "fallback"

        return {
            "filename": "landing_page_es.md",
            "content": content,
            "is_fallback": llm_res.is_fallback,
            "provider": llm_res.provider,
            "mode": llm_res.mode,
            "model": llm_res.model,
            "error_detail": llm_res.error_detail
        }
