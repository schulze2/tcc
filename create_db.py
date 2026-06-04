from app import create_app
from app.extensions import db
from app.models.cargo import Cargo

app = create_app()

with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")
    cargos_iniciais = [
        "Advogado",
        "Órgão Público",
        "Pessoa Jurídica",
        "Juiz",
        "Promotor",
        "Defensor Público",
        "Estagiario",
    ]

    existindo = {c.cargo for c in Cargo.query.all()}

    adicionando = [Cargo(cargo=nome)
                   for nome in cargos_iniciais if nome not in existindo]

    if adicionando:
        db.session.add_all(adicionando)
        db.session.commit()
        print(f"Cargos iniciais adicionados: {[c.cargo for c in adicionando]}")
    else:
        print("Todos os cargos iniciais já existem no banco de dados.")
