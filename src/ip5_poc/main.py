from fastapi import FastAPI
from oscal_pydantic.document import Document
import oscal_pydantic.catalog as catalog
import oscal_pydantic.core.common as common
import uuid

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/catalog")
def read_catalog():

    # Construct section T - Technik
    si001_t2 = catalog.Group(
        id="t2",
        title="Technik",
        parts=[
            # TODO Somehow schema error
            # catalog.BasePart(
            #     id="t2.1_gdn",
            #     name="guidance",
            #     prose="Letztlich kann diese Anforderung auch als «Best Practices» verstanden bzw. davon abgeleitet werden. Aufgrund ihrer Wichtigkeit wird sie hier aber separat aufgeführt."
            # )
        ],
        controls=[
            catalog.Control(
                id="t2.1",
                title="Konfiguration und Einstellungen",
                parts=[
                    catalog.BasePart(
                        id="t2.1_a_stm",
                        name="statement",
                        prose="Das Schutzobjekt muss vor der ersten Inbetriebnahme konfiguriert und eingestellt sein, dass  es vor unberechtigtem Zugriff geschützt ist"
                    ),
                    catalog.BasePart(
                        id="t2.1_b_stm",
                        name="statement",
                        prose="Das Schutzobjekt muss vor der ersten Inbetriebnahme konfiguriert und eingestellt sein, dass es soweit technisch möglich gehärtet ist und in einer zur Aufgabenerfüllung erforderlichen und vom Benutzer nicht veränderbaren Minimalkonfiguration betrieben wird (d.h. nicht genutzte Schnittstellen, Module und Funktionen müssen deaktiviert sein)"
                    ),
                    catalog.BasePart(
                        id="t2.1_c_stm",
                        name="statement",
                        prose="Das Schutzobjekt muss vor der ersten Inbetriebnahme konfiguriert und eingestellt sein, dass wichtige sicherheitsrelevante Aktivitäten und Ereignisse (mit Zeitangaben) aufgezeichnet und zeitnah ausgewertet werden"
                    )
                ]
            )
        ]
    )


    # Construct si001 as a whole
    si001 = Document(
        catalog=catalog.Catalog(
            uuid=uuid.uuid4(),
            metadata=common.Metadata(
                title="Si001",
                version="0.1.0",
                oscal_version="2.0",
                published="2024-05-08T00:00:00.000-00:00"
            ),
            groups=[
                si001_t2
            ],
            back_matter=common.BackMatter()
        )
    )
    return si001.model_dump(exclude_unset=True)