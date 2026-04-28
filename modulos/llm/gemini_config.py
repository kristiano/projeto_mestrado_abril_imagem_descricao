# gemini_config.py
# Configuração dinâmica do modelo Gemini

import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
import google.generativeai as genai
import time
from google.api_core.exceptions import ResourceExhausted

class QuotaExceededError(Exception):
    """Custom exception indicating Gemini API quota has been exceeded."""
    pass

_original_generate_content = genai.GenerativeModel.generate_content

def _generate_content_with_retry(self, *args, **kwargs):
    """Wrap generate_content with retry logic for quota limits.
    Retries up to 3 times with incremental backoff. If quota is still exceeded,
    raises QuotaExceededError with a helpful message.
    """
    max_attempts = 3
    for attempt in range(max_attempts + 1):
        try:
            return _original_generate_content(self, *args, **kwargs)
        except ResourceExhausted as e:
            if attempt == max_attempts:
                # After final attempt, raise custom error
                raise QuotaExceededError(
                    "Quota exceeded for Gemini API requests. "
                    "Please check your plan or try again later."
                ) from e
            # incremental backoff: 15s, 30s, 45s
            espera = (attempt + 1) * 15
            print(f"\n[!] Limite de cota da API (ResourceExhausted) atingido. Aguardando {espera} segundos antes de tentar novamente (tentativa {attempt+1}/{max_attempts})...")
            time.sleep(espera)

genai.GenerativeModel.generate_content = _generate_content_with_retry

load_dotenv()


def get_api_key() -> str:
    """
    Obtém a API key do arquivo .env.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY não encontrada no arquivo .env. "
            "Verifique se a chave está configurada corretamente."
        )
    return api_key


from typing import Optional

def criar_modelo(system_instruction: Optional[str] = None) -> genai.GenerativeModel:
    """
    Configura a SDK e retorna um modelo Gemini disponível para uso.
    Descobre dinamicamente um modelo que suporte generateContent.
    """
    api_key = get_api_key()
    genai.configure(api_key=api_key)

    modelos_disponiveis = []
    for m in genai.list_models():
        if "generateContent" in getattr(m, "supported_generation_methods", []):
            modelos_disponiveis.append(m.name)

    if not modelos_disponiveis:
        raise RuntimeError(
            "Nenhum modelo com suporte a 'generateContent' foi encontrado "
            "para esta API key. Verifique se sua conta tem acesso aos "
            "modelos do Gemini."
        )

    nome_modelo = modelos_disponiveis[0]
    print(f"Usando modelo: {nome_modelo}")

    return genai.GenerativeModel(
        model_name=nome_modelo,
        system_instruction=system_instruction
    )