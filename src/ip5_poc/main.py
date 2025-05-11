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

    # Construct section O - Organisation
    si001_organisation = catalog.Group(
        id="organisation",
        title="Organisation",
        controls=[
            # TODO: Add controls here
        ]
    )

    # Construct section P - Personal
    si001_personal = catalog.Group(
        id="personal",
        title="Personal",
        controls=[
            # TODO: Add controls here
        ]
    )

    # Construct section T - Technik
    si001_technik = catalog.Group(
        id="technik",
        title="Technik",
        controls=[
            catalog.Control(
                id="t1",
                title="Betrieb",
                parts=[
                    catalog.BasePart(
                        id="t1_gdn",
                        name="guidance",
                        prose="Der Stand der Technik kann im Einzelfall nicht präzis definiert werden und muss z.B. mit den zuständigen Informatiksicherheitsbeauftragten (ISBO und ISBD) ermittelt werden. Für grundsätzliche Fragen und Technologieabschätzungen kann auch das NCSC beigezogen bzw. https://intranet.ncsc.admin.ch/ncscintra/de/home/dokumentation/empfehlung_technologiebetrachtung.htm konsultiert werden."
                    ),
                    catalog.BasePart(
                        id="t1_stm",
                        name="statement",
                        prose="Das Schutzobjekt muss dem Stand der Technik entsprechend und unter Berücksichtigung von branchenüblichen Sicherheitsvorgaben und -empfehlungen («Best Practices») betrieben werden."
                    )
                ]
            ),
            catalog.Control(
                id="t2.1",
                title="Konfiguration und Einstellungen",
                parts=[
                    catalog.BasePart(
                        id="t2.1_gdn",
                        name="guidance",
                        prose="Letztlich kann diese Anforderung auch als «Best Practices» verstanden bzw. davon abgeleitet werden. Aufgrund ihrer Wichtigkeit wird sie hier aber separat aufgeführt."
                    ),
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
            ),
            catalog.Control(
                id="t2.2",
                title="Sicherheitskonfigurationen und -einstellungen",
                parts=[
                    catalog.BasePart(
                        id="t2.2_gdn",
                        name="guidance",
                        prose="Eine Härtung im Sinne von Anforderung T2.1 macht nur dann Sinn, wenn Sicherheitskonfigurationen und -einstellungen nur autorisiert aktiviert, geändert, deaktiviert und deinstalliert werden dürfen."
                    ),
                    catalog.BasePart(
                        id="t2.2_stm",
                        name="statement",
                        prose="Sicherheitskonfigurationen und -einstellungen dürfen nur autorisiert aktiviert, geändert, deaktiviert und deinstalliert werden."
                    )
                ]
            ),
            catalog.Control(
                id="t3",
                title="Produktive Umgebung",
                parts=[
                    catalog.BasePart(
                        id="t3_gdn",
                        name="guidance",
                        prose="Grundsätzlich ist eine physische Trennung zu bevorzugen. Falls das nicht möglich oder wirtschaftlich nicht vertretbar ist, kann eine logische Trennung erfolgen. Allerdings müssen dann die zur logischen Trennung eingesetzten Sicherheitsvorkehrungen und -massnahmen begründet und dokumentiert sein."
                    ),
                    catalog.BasePart(
                        id="t3_stm",
                        name="statement",
                        prose="Die produktive Umgebung des Schutzobjekts muss von allenfalls vorhandenen nicht produktiven Umgebungen (z.B. für Entwicklung und/oder Test) getrennt sein. Erfolgt die Trennung logisch, müssen die entsprechenden Sicherheitsvorkehrungen und -massnahmen begründet und dokumentiert sein."
                    )
                ]
            ),
            catalog.Control(
                id="t4",
                title="Schwachstellen und Verwundbarkeiten",
                parts=[
                    catalog.BasePart(
                        id="t4_gdn",
                        name="guidance",
                        prose="Idealerweise ist das Schutzobjekt in ein möglichst vollständiges und automatisiertes Verwundbarkeitsmanagement einzubinden."
                    ),
                    catalog.BasePart(
                        id="t4_stm",
                        name="statement",
                        prose="Das Schutzobjekt muss im Hinblick auf Schwachstellen und Verwundbarkeiten vor seiner Inbetriebnahme und in Abhängigkeit seines Schutzbedarfs und Exposition gegenüber dem Internet auch während des laufenden Betriebs regelmässig und vorzugsweise automatisiert überprüft werden (z.B. mit einem Security Scanner). Für kritische Schwachstellen und Verwundbarkeiten ist das NCSC beizuziehen."
                    )
                ]
            ),
            catalog.Control(
                id="t5.1",
                title="Authentifikation und Autorisation",
                parts=[
                    catalog.BasePart(
                        id="t5.1_gdn",
                        name="guidance",
                        prose="Grundsätzlich muss die Zugriffskontrolle vollständig sein und den erwähnten Prinzipien folgen. Dabei kann die Authentifikation lokal oder über eine oder mehrere Netzwerkverbindungen erfolgen. Im zweiten Fall wird die Authentifikation in ihrer Gesamtheit betrachtet (d.h. lokale Authentifikation auf einem Endgerät und allfällige Authentifikationen auf Proxy Servern)."
                    ),
                    catalog.BasePart(
                        id="t5.1_stm",
                        name="statement",
                        prose="Jeder Zugriff auf ein Schutzobjekt muss seinem Schutzbedarf entsprechend authentifiziert und gemäss dem «Least Privilege»- bzw. «Need-to-Know»-Prinzip autorisiert sein."
                    )
                ]
            ),
            catalog.Control(
                id="t5.2",
                title="Zugriffsrechte",
                parts=[
                    catalog.BasePart(
                        id="t5.2_gdn",
                        name="guidance",
                        prose="Im Rahmen des hier angesprochenen Prozesses muss die Gewaltentrennung zwischen Bewilligung und Vergabe von Zugriffsrechten wenn möglich und sinnvoll berücksichtigt und mit dokumentiert sein. Damit die Zugriffsrechte an veränderte Verhältnisse angepasst werden können (z.B. wenn die Anstellung, der Auftrag oder eine entsprechende Nutzungsvereinbarung der Mitarbeitenden geändert oder beendet wird) sollte eine Verknüpfung mit den HR Prozess definiert sein."
                    ),
                    catalog.BasePart(
                        id="t5.2_stm",
                        name="statement",
                        prose="Alle Zugriffsrechte auf das Schutzobjekt müssen im Rahmen eines definierten und dokumentierten Prozesses verwaltet und stets aktuell gehalten werden. Insbesondere müssen die Rechte mindestens jährlich in Bezug auf Notwendigkeit und Richtigkeit überprüft und nicht mehr benötigte Rechte (bzw. Konti) entfernt werden."
                    )
                ]
            ),
            catalog.Control(
                id="t5.3",
                title="Authentifikations- und Identitätsnachweismittel",
                parts=[
                    catalog.BasePart(
                        id="t5.3_gdn",
                        name="guidance",
                        prose="Diese Anforderung trägt insbesondere der Tatsache Rechnung, dass beim Einsatz eines Authentifikations- und Identitätsnachweismittels die entsprechenden Verwaltungsprozesse mindestens ebenso wichtig sind, wie das eingesetzte Mittel (aus technischer Sicht)."
                    ),
                    catalog.BasePart(
                        id="t5.3_stm",
                        name="statement",
                        prose="Für das Schutzobjekt dürfen nur Authentifikations- und Identitätsnachweismittel eingesetzt werden, die im Rahmen eines definierten und dokumentierten Prozesses verwaltet werden, der den gesamten Life Cycle des Mittels (inkl. Zugriffsmöglichkeiten für Notfälle, Sperrung, Zurücksetzung, Revozierung und Entsorgung) mit abdeckt."
                    )
                ]
            ),
            catalog.Control(
                id="t6.1",
                title="Benutzerauthentifikation (APS/Server-System)",
                parts=[
                    catalog.BasePart(
                        id="t6.1_gdn",
                        name="guidance",
                        prose="Die Notwendigkeit einer 2-Faktoren-Authentisierung ergibt sich aus dem BRB vom 04. Juni 2010. Für die Angestellten des Bundes werden dabei Klasse-B-Zertifikate der SG-PKI eingesetzt. Bei einem Server-System bezieht sich die Benutzerauthentifikation auf die Betriebssystemebene."
                    ),
                    catalog.BasePart(
                        id="t6.1_stm",
                        name="statement",
                        prose="Die Benutzerauthentifikation gegenüber einem APS oder einem Server-System muss auf der Basis eines Authentifikations- und Identitätsnachweismittels mindestens der Sicherheitsstufe «mittel» gemäss Anhang B bzw. einer 2-Faktoren-Authentifikation erfolgen."
                    )
                ]
            ),
            catalog.Control(
                id="t6.2",
                title="Benutzerauthentifikation (MDM-System)",
                parts=[
                    catalog.BasePart(
                        id="t6.2_gdn",
                        name="guidance",
                        prose="Die konzeptionellen Unterschiede zwischen einem Passwort und einer PIN sind in der Technologiebetrachtung «Passwörter vs. PINs» vom 29. Juni 2012 ausgeführt. Ein trivialer PIN ist z.B. eine Benutzer-Nummer, ein Geburtsdatum oder eine Ziffernfolge wie 111111, 123456 oder 654321."
                    ),
                    catalog.BasePart(
                        id="t6.2_stm",
                        name="statement",
                        prose="Die Benutzerauthentifikation gegenüber einem MDM-System muss auf der Basis der vom jeweiligen Betriebssystem unterstützten Verfahren erfolgen, wie z.B. PIN oder biometrische Authentifikation (z.B. Touch ID oder Face ID für iOS-Geräte). Ein PIN muss mindestens 6 Zeichen enthalten und darf nicht trivial sein."
                    )
                ]
            ),
            catalog.Control(
                id="t6.3",
                title="Benutzerauthentifikation (Netzwerkkomponente)",
                parts=[
                    catalog.BasePart(
                        id="t6.3_gdn",
                        name="guidance",
                        prose="Weil das Missbrauchspotential beim Zugriff auf eine Netzwerkkomponente gross ist, ergibt sich die Notwendigkeit eines Authentifikations- und Identitätsnachweismittels mindestens der Sicherheitsstufe «hoch»."
                    ),
                    catalog.BasePart(
                        id="t6.3_stm",
                        name="statement",
                        prose="Die Benutzerauthentifikation gegenüber einer Netzwerkkomponente muss auf der Basis eines Authentifikations- und Identitätsnachweismittels mindestens der Sicherheitsstufe «hoch» gemäss Anhang B erfolgen."
                    )
                ]
            ),
            catalog.Control(
                id="t8.1",
                title="Administrative Zugriffe",
                parts=[
                    catalog.BasePart(
                        id="t8.1_gdn",
                        name="guidance",
                        prose="Die kryptografische Absicherung und Aufzeichnung bzw. Auswertung erscheint bei administrativen Zugriffen besonders wichtig, damit nicht autorisierte Aktivitäten verhindert oder erkannt werden können. Dabei muss sich die kryptografische Absicherung sowohl auf die Authentifikation als auch den Vertraulichkeits- und Integritätsschutz der Daten beziehen."
                    ),
                    catalog.BasePart(
                        id="t8.1_stm",
                        name="statement",
                        prose="Administrative Zugriffe auf das Schutzobjekt müssen auf eine dokumentierte und kontrollierte Art und Weise erfolgen. Insbesondere müssen solche Zugriffe kryptografisch abgesichert sein und nachvollziehbar aufgezeichnet und ausgewertet werden."
                    )
                ]
            ),
            catalog.Control(
                id="t8.2",
                title="Administrative IT-Systeme",
                parts=[
                    catalog.BasePart(
                        id="t8.2_gdn",
                        name="guidance",
                        prose="Diese Anforderungen ergeben sich primär aus dem «Mitigation Credential Theft» (MCT)-Projekt. Kurzlebige Zugriffsrechte lassen sich idealerweise für Konti umsetzen, die im Rahmen einer Privileged Access Management (PAM) Lösung verwaltet werden. Solche Rechte sind nur für die Dauer einer bestimmten Administrationstätigkeit gültig."
                    ),
                    catalog.BasePart(
                        id="t8.2_stm",
                        name="statement",
                        prose="Die für administrative Zugriffe verwendeten IT-Systeme müssen für diese Aufgabe ausgelegt sein und vorzugsweise in einer Management Zone betrieben werden. Die Nutzung der entsprechenden (privilegierten) Konti muss einer Person zugeordnet werden können."
                    )
                ]
            ),
            catalog.Control(
                id="t8.3",
                title="Fernzugriffe durch externe Anbieter",
                parts=[
                    catalog.BasePart(
                        id="t8.3_gdn",
                        name="guidance",
                        prose="Diese Anforderung ist neu formuliert und entspricht inhaltlich den Anforderungen aus den bisher geltenden Sicherheitsvorgaben."
                    ),
                    catalog.BasePart(
                        id="t8.3_a_stm",
                        name="statement",
                        prose="Der Inhaber des Objekts muss einverstanden sein und bezüglich möglicher Amtsgeheimnisverletzungen gemäss den amts- bzw. departementsspezifischen Prozessen eingewilligt haben (vgl. [Si001-Hi03, Si001-Hi04])."
                    ),
                    catalog.BasePart(
                        id="t8.3_b_stm",
                        name="statement",
                        prose="Der Zugriff muss über ein dediziertes Konto erfolgen und die entsprechende Benutzerauthentifikation auf einem Authentifikations- und Identitätsnachweismittel mindestens der Stufe «mittel» gemäss Anhang B basieren."
                    ),
                    catalog.BasePart(
                        id="t8.3_c_stm",
                        name="statement",
                        prose="Die Nutzung dieses Kontos muss zeitlich begrenzt sein und überwacht werden."
                    ),
                    catalog.BasePart(
                        id="t8.3_d_stm",
                        name="statement",
                        prose="Wenn technisch möglich, muss der Zugriff über einen Jumphost erfolgen."
                    ),
                    catalog.BasePart(
                        id="t8.3_e_stm",
                        name="statement",
                        prose="Die netzwerktechnische Verbindung für den Zugriff muss kryptografisch abgesichert sein (z.B. mit Hilfe von SSH)."
                    ),
                    catalog.BasePart(
                        id="t8.3_f_stm",
                        name="statement",
                        prose="Die Auditierbarkeit der externalisierten Prozesse muss jederzeit sichergestellt sein."
                    ),
                ]
            )
        ]
    )

    # Construct section I - Informationen (Daten)
    si001_information = catalog.Group(
        id="information",
        title="Information",
        controls=[
            # TODO: Add controls here
        ]
    )

    # Construct section S - IT-Systeme
    si001_systeme = catalog.Group(
        id="systeme",
        title="IT-Systeme",
        controls=[
            # TODO: Add controls here
        ]
    )

    # Construct section A - Anwendungen
    si001_anwendungen = catalog.Group(
        id="anwendungen",
        title="Anwendungen",
        controls=[
            # TODO: Add controls here
        ]
    )

    # Construct section Z - Zonen
    si001_zonen = catalog.Group(
        id="zonen",
        title="Zonen",
        controls=[
            # TODO: Add controls here
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
                si001_organisation,
                si001_personal,
                si001_technik,
                si001_information,
                si001_systeme,
                si001_anwendungen,
                si001_zonen
            ],
            back_matter=common.BackMatter()
        )
    )
    return si001.model_dump(exclude_unset=True)