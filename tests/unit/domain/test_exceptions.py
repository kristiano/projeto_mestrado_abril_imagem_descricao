from domain.shared.exceptions import DomainError, RecursoNaoEncontradoError


def test_domain_error_guarda_code_message_e_details() -> None:
    exc = RecursoNaoEncontradoError(
        code="ALUNO_NAO_ENCONTRADO",
        message="Aluno não encontrado.",
        details={"aluno_id": "123"},
    )

    assert exc.code == "ALUNO_NAO_ENCONTRADO"
    assert exc.message == "Aluno não encontrado."
    assert exc.details == {"aluno_id": "123"}
    assert isinstance(exc, DomainError)


def test_domain_error_details_e_opcional() -> None:
    exc = RecursoNaoEncontradoError(code="X", message="Y")

    assert exc.details is None
