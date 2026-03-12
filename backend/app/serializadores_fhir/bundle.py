from app.serializadores_fhir.bundle_geral import (
    build_transaction_bundle,
    validate_bundle_for_hapi_operation,
)


def montar_bundle_agendamento(a):
    if not all([a.paciente, a.profissional, a.local, a.especialidade]):
        raise ValueError("Agendamento sem relacionamentos obrigatórios para gerar Bundle.")

    bundle = build_transaction_bundle(
        pacientes=[a.paciente],
        profissionais=[a.profissional],
        agendamentos=[a],
        locais=[a.local],
    )

    validate_bundle_for_hapi_operation(
        bundle=bundle,
        operation="post_transaction",
    )
    return bundle
