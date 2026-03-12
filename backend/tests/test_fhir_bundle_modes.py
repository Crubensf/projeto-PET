from __future__ import annotations

import os
import sys
import unittest
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace

# Permite execução com: python3 -m unittest backend.tests.test_fhir_bundle_modes
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.serializadores_fhir.bundle import montar_bundle_agendamento
from app.serializadores_fhir.bundle_geral import (
    BundleValidationError,
    build_patient_appointments_transaction_bundle,
    build_searchset_bundle,
    build_transaction_bundle,
    validate_bundle_for_hapi_operation,
)


class BundleModesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.paciente = SimpleNamespace(
            id=4,
            nome="Caio R Feitosa",
            data_nascimento=date(2001, 2, 2),
            cpf="00000000004",
            cartao_sus="123457891234567",
            telefone="89981248316",
            endereco="Rua antonio benedito",
            municipio="Picos",
            nome_mae="Celia Cristina",
        )
        self.profissional = SimpleNamespace(
            id=23,
            nome="Dra. Renata Ribeiro",
            crm="12345",
            crm_uf="PI",
        )
        self.local = SimpleNamespace(
            id=1,
            nome="UBS Canto da Várzea",
            endereco="Av. Principal, 1000",
            municipio="Picos",
        )
        self.especialidade = SimpleNamespace(
            codigo="ENDOCRINOLOGIA",
            nome="Endocrinologia",
        )
        self.agendamento = SimpleNamespace(
            id=6,
            inicio=datetime(2026, 1, 29, 16, 30, 0),
            status="agendado",
            modalidade="PRESENCIAL",
            paciente_id=self.paciente.id,
            profissional_id=self.profissional.id,
            local_id=self.local.id,
            paciente=self.paciente,
            profissional=self.profissional,
            local=self.local,
            especialidade=self.especialidade,
        )

    def _inputs(self):
        return {
            "pacientes": [self.paciente],
            "profissionais": [self.profissional],
            "agendamentos": [self.agendamento],
            "locais": [self.local],
        }

    def test_searchset_contract_is_preserved(self) -> None:
        bundle = build_searchset_bundle(**self._inputs())

        self.assertEqual(bundle.get("resourceType"), "Bundle")
        self.assertEqual(bundle.get("type"), "searchset")
        self.assertIn("total", bundle)
        self.assertIsInstance(bundle.get("entry"), list)
        self.assertEqual(bundle["total"], len(bundle["entry"]))

        for entry in bundle["entry"]:
            self.assertIn("search", entry)
            self.assertNotIn("request", entry)

    def test_searchset_is_rejected_for_transaction_post(self) -> None:
        bundle = build_searchset_bundle(**self._inputs())
        with self.assertLogs(
            "app.serializadores_fhir.bundle_geral",
            level="WARNING",
        ) as logs:
            with self.assertRaisesRegex(
                BundleValidationError,
                "FHIR_BUNDLE_SEARCHSET_NOT_ALLOWED",
            ):
                validate_bundle_for_hapi_operation(
                    bundle=bundle,
                    operation="post_transaction",
                )
        self.assertTrue(any("post_transaction" in item for item in logs.output))

    def test_transaction_bundle_is_accepted_for_transaction_post(self) -> None:
        bundle = build_transaction_bundle(**self._inputs())

        validate_bundle_for_hapi_operation(
            bundle=bundle,
            operation="post_transaction",
        )
        self.assertEqual(bundle.get("resourceType"), "Bundle")
        self.assertEqual(bundle.get("type"), "transaction")
        self.assertNotIn("total", bundle)

        for entry in bundle.get("entry", []):
            self.assertIn("fullUrl", entry)
            self.assertIn("resource", entry)
            self.assertIn("request", entry)
            self.assertNotIn("search", entry)
            self.assertTrue(entry["fullUrl"].startswith("urn:uuid:"))
            self.assertEqual(entry["request"]["method"], "POST")
            self.assertEqual(
                entry["request"]["url"],
                entry["resource"]["resourceType"],
            )

    def test_invalid_bundle_returns_descriptive_error(self) -> None:
        bundle = build_transaction_bundle(**self._inputs())
        bundle["entry"][0].pop("request", None)

        with self.assertLogs(
            "app.serializadores_fhir.bundle_geral",
            level="WARNING",
        ) as logs:
            with self.assertRaisesRegex(
                BundleValidationError,
                "FHIR_BUNDLE_ENTRY_REQUEST_MISSING",
            ):
                validate_bundle_for_hapi_operation(
                    bundle=bundle,
                    operation="post_transaction",
                )
        self.assertTrue(any("entry[0]" in item for item in logs.output))

    def test_individual_transaction_bundle_uses_urn_references(self) -> None:
        bundle = montar_bundle_agendamento(self.agendamento)
        validate_bundle_for_hapi_operation(
            bundle=bundle,
            operation="post_transaction",
        )

        appointment = next(
            entry["resource"]
            for entry in bundle["entry"]
            if entry["resource"].get("resourceType") == "Appointment"
        )
        references = [
            part.get("actor", {}).get("reference")
            for part in appointment.get("participant", [])
        ]

        full_urls = {
            entry.get("fullUrl")
            for entry in bundle.get("entry", [])
            if isinstance(entry, dict)
        }
        for ref in references:
            self.assertIsInstance(ref, str)
            self.assertTrue(ref.startswith("urn:uuid:"))
            self.assertIn(ref, full_urls)

    def test_patient_appointments_transaction_bundle(self) -> None:
        bundle = build_patient_appointments_transaction_bundle(
            paciente=self.paciente,
            profissionais=[self.profissional],
            agendamentos=[self.agendamento],
            locais=[self.local],
        )
        self.assertEqual(bundle.get("resourceType"), "Bundle")
        self.assertEqual(bundle.get("type"), "transaction")
        self.assertIsNone(bundle.get("total"))

        resource_types = [
            entry.get("resource", {}).get("resourceType")
            for entry in bundle.get("entry", [])
        ]
        self.assertIn("Patient", resource_types)
        self.assertIn("Practitioner", resource_types)
        self.assertIn("Appointment", resource_types)
        self.assertIn("Location", resource_types)

    def test_broken_appointment_reference_is_rejected(self) -> None:
        agendamento_invalido = SimpleNamespace(**vars(self.agendamento))
        agendamento_invalido.profissional_id = 999

        with self.assertRaisesRegex(ValueError, "Reference Practitioner/999"):
            build_transaction_bundle(
                pacientes=[self.paciente],
                profissionais=[self.profissional],
                agendamentos=[agendamento_invalido],
                locais=[self.local],
            )

    def test_missing_referenced_resource_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Reference Practitioner/23"):
            build_transaction_bundle(
                pacientes=[self.paciente],
                profissionais=[],
                agendamentos=[self.agendamento],
                locais=[self.local],
            )


if __name__ == "__main__":
    unittest.main()
