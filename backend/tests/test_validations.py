from __future__ import annotations

import unittest
from datetime import date, timedelta

from pydantic import ValidationError

from app.core.validators import (
    sanitize_cep,
    sanitize_cns,
    sanitize_cpf,
    sanitize_phone,
)
from app.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate
from app.schemas.paciente import PacienteCreate
from app.schemas.profissional import ProfissionalCreate


class ValidationRulesTestCase(unittest.TestCase):
    def test_sanitize_cpf(self) -> None:
        self.assertEqual(sanitize_cpf("123.456.789-01"), "12345678901")
        with self.assertRaises(ValueError):
            sanitize_cpf("123")

    def test_sanitize_cns(self) -> None:
        self.assertEqual(sanitize_cns("123 4567 8912 3456"), "123456789123456")
        with self.assertRaises(ValueError):
            sanitize_cns("123")

    def test_sanitize_phone(self) -> None:
        self.assertEqual(sanitize_phone("+55 (89) 98888-7777"), "89988887777")
        self.assertEqual(sanitize_phone("(89) 3333-2222"), "8933332222")
        with self.assertRaises(ValueError):
            sanitize_phone("999")

    def test_sanitize_cep(self) -> None:
        self.assertEqual(sanitize_cep("64600-000"), "64600000")
        with self.assertRaises(ValueError):
            sanitize_cep("64000")

    def test_paciente_create_validation(self) -> None:
        payload = {
            "nome": "Paciente Teste",
            "cpf": "123.456.789-01",
            "cartao_sus": "123 4567 8912 3456",
            "telefone": "+55 (89) 98888-7777",
            "data_nascimento": "2000-01-01",
            "municipio": "Picos",
            "endereco": "Rua A, 100",
            "nome_mae": "Maria Teste",
        }
        p = PacienteCreate(**payload)
        self.assertEqual(p.cpf, "12345678901")
        self.assertEqual(p.cartao_sus, "123456789123456")
        self.assertEqual(p.telefone, "89988887777")

        future_payload = dict(payload)
        future_payload["data_nascimento"] = str(date.today() + timedelta(days=1))
        with self.assertRaises(ValidationError):
            PacienteCreate(**future_payload)

    def test_agendamento_ids_must_be_positive(self) -> None:
        with self.assertRaises(ValidationError):
            AgendamentoCreate(
                paciente_id=0,
                profissional_id=1,
                especialidade_id=1,
                local_id=1,
                inicio="2026-03-12T10:00:00",
                modalidade="PRESENCIAL",
                status="agendado",
            )

        with self.assertRaises(ValidationError):
            AgendamentoUpdate(paciente_id=-10)

    def test_profissional_validation(self) -> None:
        prof = ProfissionalCreate(
            nome="Profissional Teste",
            especialidade_id=1,
            crm="12.345-6",
            crm_uf="pi",
            telefone="+55 (89) 98888-7777",
        )
        self.assertEqual(prof.crm, "123456")
        self.assertEqual(prof.crm_uf, "PI")
        self.assertEqual(prof.telefone, "89988887777")

        with self.assertRaises(ValidationError):
            ProfissionalCreate(
                nome="Profissional Inválido",
                especialidade_id=0,
            )


if __name__ == "__main__":
    unittest.main()
