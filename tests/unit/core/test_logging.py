import json
import logging

from core.logging import JsonFormatter, request_id_var


def _formatar(record: logging.LogRecord) -> dict[str, str]:
    return json.loads(JsonFormatter().format(record))


def _record(msg: str = "mensagem de teste") -> logging.LogRecord:
    return logging.LogRecord(
        name="teste",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=(),
        exc_info=None,
    )


def test_formata_como_json_com_campos_esperados() -> None:
    payload = _formatar(_record())

    assert payload["level"] == "INFO"
    assert payload["logger"] == "teste"
    assert payload["message"] == "mensagem de teste"
    assert "timestamp" in payload


def test_inclui_request_id_quando_definido_no_contexto() -> None:
    token = request_id_var.set("abc-123")
    try:
        payload = _formatar(_record())
    finally:
        request_id_var.reset(token)

    assert payload["request_id"] == "abc-123"


def test_omite_request_id_fora_de_uma_requisicao() -> None:
    payload = _formatar(_record())

    assert "request_id" not in payload
