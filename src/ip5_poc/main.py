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
            catalog.Control(
                id="o1",
                title="Verantwortlichkeit",
                parts=[
                    catalog.BasePart(
                        id="o1_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss eine verantwortliche Person (innerhalb der verantwortlichen VE) als Schutzobjektverantwortliche/r definiert sein. Diese Person ist für die Umsetzung dieser Vorgabe zuständig. Sie muss sich ihrer Verantwortung bewusst und fachtechnisch in der Lage sein, die Verantwortung auch wahrzunehmen."
                    ),
                    catalog.BasePart(
                        id="o1_gdn",
                        name="guidance",
                        prose="Für eine Anwendung ist das die oder der Anwendungs-Verantwortliche gemäss der Rollenbeschreibung der Informatikprozesse der Bundesverwaltung (vgl. https://intranet.dti.bk.admin.ch/isb_kp/de/home/ikt-vorgaben/prozesse-methoden/p000-informatikprozesse_in_der_bundesverwaltung.html). Für ein anderes Schutzobjekt muss in analoger Art und Weise eine verantwortliche Person (innerhalb der für das Schutzobjekt verantwortlichen VE) bestimmt werden."
                    )
                ]
            ),
            catalog.Control(
                id="o2.1",
                title="Dokumentation",
                parts=[
                    catalog.BasePart(
                        id="o2.1_a_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss eine aktuelle und mit den beteiligten LE abgeglichene Dokumentation vorliegen. Dabei muss die Dokumentation die gesamte Lebensdauer («Life Cycle») des Objekts abdecken und insbesondere auch die Lieferkette («Supply Chain») abdecken."
                    ),
                    catalog.BasePart(
                        id="o2.1_b_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss eine aktuelle und mit den beteiligten LE abgeglichene Dokumentation vorliegen. Dabei muss die Dokumentation die gesamte Lebensdauer («Life Cycle») des Objekts abdecken und insbesondere auch die physischen Schutzmassnahmen abdecken, wobei die Notwendigkeit von baulichen und technischen Massnahmen zum physischen Schutz von IT-Systemen dort, wo erforderlich, mit dem BBL, der armasuisse bzw. dem Bundessicherheitsdienst abgeklärt sein muss."
                    ),
                    catalog.BasePart(
                        id="o2.1_c_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss eine aktuelle und mit den beteiligten LE abgeglichene Dokumentation vorliegen. Dabei muss die Dokumentation die gesamte Lebensdauer («Life Cycle») des Objekts abdecken und insbesondere auch die sicherheitsrelevanten Komponenten, Funktionen und Einstellungen abdecken."
                    ),
                    catalog.BasePart(
                        id="o2.1_d_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss eine aktuelle und mit den beteiligten LE abgeglichene Dokumentation vorliegen. Dabei muss die Dokumentation die gesamte Lebensdauer («Life Cycle») des Objekts abdecken und insbesondere auch die Schlüsselverwaltung beim Einsatz kryptografischer Verfahren abdecken."
                    ),
                    catalog.BasePart(
                        id="o2.1_e_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss eine aktuelle und mit den beteiligten LE abgeglichene Dokumentation vorliegen. Dabei muss die Dokumentation die gesamte Lebensdauer («Life Cycle») des Objekts abdecken und insbesondere auch die Modalitäten und Prozesse bei Änderung (im Rahmen des «Change Managements»), Reparatur, Entsorgung und Verlust abdecken."
                    ),
                    catalog.BasePart(
                        id="o2.1_f_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss eine aktuelle und mit den beteiligten LE abgeglichene Dokumentation vorliegen. Dabei muss die Dokumentation die gesamte Lebensdauer («Life Cycle») des Objekts abdecken und insbesondere auch die vertraglichen Vereinbarungen abdecken."
                    ),
                    catalog.BasePart(
                        id="o2.1_g_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss eine aktuelle und mit den beteiligten LE abgeglichene Dokumentation vorliegen. Dabei muss die Dokumentation die gesamte Lebensdauer («Life Cycle») des Objekts abdecken und insbesondere auch die Audit-Prozesse und -Aktivitäten zur Kontrolle der Umsetzung und Einhaltung dieser Vorgabe abdecken."
                    ),
                    catalog.BasePart(
                        id="o2.1_gdn",
                        name="guidance",
                        prose="Eine umfassende und möglichst vollständige Dokumentation der hier aufgeführten Punkte zum Schutzobjekt ist erforderlich, damit Aussagen über die Sicherheit gemacht und entsprechende Schlussfolgerungen gezogen werden können. Die Liste der Punkte ist nicht abschliessend, d.h. wenn es zu anderen Punkten Bemerkungen zu ergänzen hat, dann ist das sehr wünschenswert."
                    )
                ]
            ),
            catalog.Control(
                id="o2.2",
                title="Dokumentation für externen Betrieb",
                parts=[
                    catalog.BasePart(
                        id="o2.2_a_stm",
                        name="statement",
                        prose="Wird das Schutzobjekt (IT-System oder Anwendung) nicht in einer Zone der Bundesverwaltung betrieben (z.B. in einer Public Cloud), muss in der Dokumentation beschrieben sein, wie in einer externen Umgebung dem Schutzbedarf des Objekts entsprochen werden kann."
                    ),
                    catalog.BasePart(
                        id="o2.2_b_stm",
                        name="statement",
                        prose="Wird das Schutzobjekt (IT-System oder Anwendung) nicht in einer Zone der Bundesverwaltung betrieben (z.B. in einer Public Cloud), muss in der Dokumentation beschrieben sein, mit welchen komplementären Sicherheitsmassnahmen sichergestellt wird, dass sich für andere Schutzobjekte der Bundesverwaltung keine zusätzlichen Bedrohungen und Risiken ergeben."
                    ),
                    catalog.BasePart(
                        id="o2.2_gdn",
                        name="guidance",
                        prose="Gemäss dem Grundsatz und Prinzip 1 (Form der Leistungserbringung) ist der externe Betrieb eines Schutzobjektes (z.B. in einer Public Cloud) zulässig, wenn in dieser Umgebung dem Schutzbedarf des Objekts entsprochen werden kann. Die Art und Weise, wie das sichergestellt ist und wie mit Hilfe von komplementären Sicherheitsmassnahmen sichergestellt ist, dass sich für andere Schutzobjekte der Bundesverwaltung keine zusätzlichen Bedrohungen und Risiken ergeben, muss hier möglichst umfassend dokumentiert sein."
                    )
                ]
            ),
            catalog.Control(
                id="o3",
                title="Geschäftskontinuität",
                parts=[
                    catalog.BasePart(
                        id="o3_stm",
                        name="statement",
                        prose="Für das Schutzobjekt muss die Geschäftskontinuität im Rahmen eines IT Service Continuity Management (ITSCM) bzw. eines Business Continuity Management (BCM) Prozesses gemäss ausgewiesenem Bedarf in der Schutzbedarfsanalyse (Schuban) sichergestellt und dokumentiert sein."
                    ),
                    catalog.BasePart(
                        id="o3_gdn",
                        name="guidance",
                        prose="Die ITSCM- und BCM-Prozesse müssen dem ausgewiesenen Bedarf entsprechen und umfassend dokumentiert sein. Dabei muss insbesondere auch der zunehmenden Gefahr von Cyberangriffen Rechnung getragen werden."
                    )
                ]
            ),
            catalog.Control(
                id="o4",
                title="Cybervorfälle",
                parts=[
                    catalog.BasePart(
                        id="o4_stm",
                        name="statement",
                        prose="Das Schutzobjekt muss in den Prozess zur Bewältigung von Cybervorfällen eingebunden sein. Bei grösseren Vorfällen werden die Arbeiten vom NCSC koordiniert."
                    ),
                    catalog.BasePart(
                        id="o4_gdn",
                        name="guidance",
                        prose="Ein Beispiel eines solchen Prozesses ist unter https://intranet.ncsc.admin.ch/dam/ncscintra/de/dokumente/partner/20210217-Bewaeltigung_Cybervorfaelle.pdf.download.pdf/20210217-Bewaeltigung_Cybervorfaelle.pdf dokumentiert. Im Falle eines Cybervorfalls muss das Schutzobjekt in einen solchen Prozess eingebunden sein, der im Übrigen auch mit den betroffenen LE und LB abgestimmt sein muss. Exemplarisch ist dieser Prozess für geeignete Schutzobjekte auch zu beüben."
                    )
                ]
            )
        ]
    )

    # Construct section P - Personal
    si001_personal = catalog.Group(
        id="personal",
        title="Personal",
        controls=[
            catalog.Control(
                id="p1.1",
                title="Sensibilisierung und Schulung",
                parts=[
                    catalog.BasePart(
                        id="p1.1_stm",
                        name="statement",
                        prose="Alle Benutzerinnen und Benutzer des Schutzobjekts müssen im Bereich der Informatiksicherheit stufen- bzw. funktionsgerecht sensibilisiert und geschult sein."
                    ),
                    catalog.BasePart(
                        id="p1.1_gdn",
                        name="guidance",
                        prose="Die Art und Weise der Sensibilisierung und Schulung ist grundsätzlich nicht festgelegt und liegt im Ermessen der verantwortlichen VE bzw. der oder des Schutzobjektverantwortlichen. Dabei müssen die Rollen im Rahmen des Schutzobjekts (z.B. Administratoren, Super-User, Benutzer, ...) berücksichtigt und entsprechende Schulungen durchgeführt werden."
                    )
                ]
            ),
            catalog.Control(
                id="p1.2",
                title="Sensibilisierung und Schulung",
                parts=[
                    catalog.BasePart(
                        id="p1.2_stm",
                        name="statement",
                        prose="Alle Benutzerinnen und Benutzer des Schutzobjekts müssen die für das Schutzobjekt relevanten Einsatzrichtlinien kennen und sind zu deren Einhaltung verpflichtet."
                    ),
                    catalog.BasePart(
                        id="p1.2_gdn",
                        name="guidance",
                        prose="Eine Übersicht über alle Einsatzrichtlinien ist unter https://intranet.dti.bk.admin.ch/isb_kp/de/home/ikt-vorgaben/einsatzrichtlinien.html verfügbar. Insbesondere gilt diese Anforderung für die Nutzung von MDM-Systemen und/oder privaten Peripheriegeräten beim Mobilen Arbeiten. Die oder der Schutzobjektverantwortliche kann für die Benutzerinnen und Benutzer die relevanten Einsatzrichtlinien festlegen."
                    )
                ]
            ),
            catalog.Control(
                id="p2",
                title="Meldepflicht",
                parts=[
                    catalog.BasePart(
                        id="p2_stm",
                        name="statement",
                        prose="Alle Benutzerinnen und Benutzer des Schutzobjekts müssen sicherheitskritische Ereignisse, wie z.B. anormales und verdächtiges Systemverhalten oder physischer Verlust, möglichst zeitnah der dafür zuständigen Stelle melden (z.B. Servicedesk des LE)."
                    ),
                    catalog.BasePart(
                        id="p2_gdn",
                        name="guidance",
                        prose="Die Festlegung der sicherheitskritischen Ereignisse kann nicht abschliessend erfolgen (ausser bei einem physischen Verlust), muss dem Schutzbedarf des Schutzobjekts entsprechen und liegt im Ermessensspielraum der verantwortlichen VE bzw. deren Informatiksicherheitsbeauftragten."
                    )
                ]
            )
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
            catalog.Control(
                id="i1",
                title="Zulässigkeit von IT-Systemen",
                parts=[
                    catalog.BasePart(
                        id="i1_stm",
                        name="statement",
                        prose="Geschäftsrelevante Informationen dürfen nur auf IT-Systemen gespeichert und verarbeitet werden, deren Inhaber entweder eine VE der Bundesverwaltung oder für die die Einhaltung der sicherheitstechnischen Anforderungen aus dieser Vorgabe vertraglich geregelt ist (z.B. im Rahmen einer Cloud-Lösung)."
                    ),
                    catalog.BasePart(
                        id="i1_gdn",
                        name="guidance",
                        prose="Mit dieser Anforderung soll sichergestellt sein, dass geschäftsrelevante Daten nur auf IT-Systemen gespeichert und verarbeitet werden, die die Bundesverwaltung technisch oder organisatorisch und rechtlich auf geeignete Art und Weise kontrollieren kann."
                    )
                ]
            ),
            catalog.Control(
                id="i2.1",
                title="Vertraulichkeit und Integrität",
                parts=[
                    catalog.BasePart(
                        id="i2.1_stm",
                        name="statement",
                        prose="Die Vertraulichkeit und Integrität von geschäftsrelevanten Informationen müssen jederzeit ihrem Schutzbedarf entsprechend und unter Berücksichtigung der physischen Gegebenheiten mit Hilfe kryptografischer Verfahren geschützt sein (gilt auch für Testdaten und zu Testzwecken eingesetzte produktive Daten). Werden Informationen verschlüsselt, dann müssen die dazu verwendeten Schlüssel so verwaltet werden, dass eine Wiederherstellung und damit eine Entschlüsselung der Informationen jederzeit möglich ist. In der Regel bedingt das eine aufwändige Schlüsselverwaltung (mit einem «Key Recovery»-Mechanismus) sowie ein periodisches Austesten der Wiederherstellbarkeit der Informationen."
                    ),
                    catalog.BasePart(
                        id="i2.1_gdn",
                        name="guidance",
                        prose="Insbesondere müssen Informationen mit erhöhtem Schutzbedarf, die auf Festplatten von physisch nicht speziell geschützten Server-Systemen gespeichert sind, mit einer Festplattenverschlüsselung geschützt sein."
                    )
                ]
            ),
            catalog.Control(
                id="i2.2",
                title="Vertraulichkeit und Integrität",
                parts=[
                    catalog.BasePart(
                        id="i2.2_stm",
                        name="statement",
                        prose="Die eingesetzten IT-Systeme müssen geeignet sein, den Schutz der Vertraulichkeit und Integrität der Informationen zu gewähren."
                    ),
                    catalog.BasePart(
                        id="i2.2_gdn",
                        name="guidance",
                        prose="So ist z.B. auf MDM-Systemen die Speicherung und Verarbeitung von als VERTRAULICH klassifizierten Informationen nicht bzw. nur im Rahmen von verschlüsselter Sprachkommunikation zulässig [E027]."
                    )
                ]
            ),
            catalog.Control(
                id="i3.1",
                title="Verfügbarkeit",
                parts=[
                    catalog.BasePart(
                        id="i3.1_stm",
                        name="statement",
                        prose="Die Verfügbarkeit von geschäftsrelevanten Informationen muss jederzeit dem Schutzbedarf entsprechend sichergestellt sein."
                    ),
                    catalog.BasePart(
                        id="i3.1_gdn",
                        name="guidance",
                        prose="Grundsätzlich wird die Verfügbarkeit von geschäftsrelevanten Informationen als übergeordnetes Ziel postuliert."
                    )
                ]
            ),
            catalog.Control(
                id="i3.2",
                title="Backup-Strategie",
                parts=[
                    catalog.BasePart(
                        id="i3.2_stm",
                        name="statement",
                        prose="Die für Informationen verantwortliche VE muss über eine Backup-Strategie verfügen und diese auch umsetzen. Diese Strategie muss ein Mehrgenerationen-Prinzip und eine offline Speicherung wichtiger Datenbestände vorsehen, so dass Daten auch im Falle von datenverschlüsselnder Malware («Ransomware») wiederhergestellt werden können."
                    ),
                    catalog.BasePart(
                        id="i3.2_gdn",
                        name="guidance",
                        prose="Ist die verantwortliche VE ein LB, kann die Backup-Strategie auch vom LE stammen. Allerdings muss die Strategie dann vom LB geprüft und als angemessen für das spezifische Schutzobjekt akzeptiert sein. Der regelmässigen Beübung der Strategie kommt in diesem Fall eine zentrale Bedeutung zu, wobei die Wiederherstellbarkeit von Daten nach einem Verlust regelmässig kontrolliert und vom LB bestätigt werden muss."
                    )
                ]
            ),
            catalog.Control(
                id="i4",
                title="Datenträger",
                parts=[
                    catalog.BasePart(
                        id="i4_stm",
                        name="statement",
                        prose="Die Datenträger, auf denen geschäftsrelevante Informationen gespeichert sind, müssen jederzeit dem Schutzbedarf der Informationen entsprechend geschützt sein. Namentlich für die Reparatur und Entsorgung von Datenträgern müssen geeignete Prozesse definiert und umgesetzt sein."
                    ),
                    catalog.BasePart(
                        id="i4_gdn",
                        name="guidance",
                        prose="Bei der Entsorgung von Datenträgern ist insbesondere darauf zu achten, dass keine Rückschlüsse auf den Inhalt oder die gespeicherten Daten möglich sind. Vergleiche dazu auch die «Empfehlung zur Vernichtung von elektronischen Datenträgern in der Bundesverwaltung» (https://intranet.ncsc.admin.ch/dam/ncscintra/de/dokumente/empfehlungen/Empfehlungen-Vernichtung_HW_V1-0-d.pdf.download.pdf/Empfehlungen-Vernichtung_HW_V1-0-d.pdf)."
                    )
                ]
            )
        ]
    )

    # Construct section S - IT-Systeme
    si001_systeme = catalog.Group(
        id="systeme",
        title="IT-Systeme",
        controls=[
            catalog.Control(
                id="s1",
                title="Zonenzugehörigkeit",
                parts=[
                    catalog.BasePart(
                        id="s1_stm",
                        name="statement",
                        prose="Das IT-System muss einer Zone zugehören und gemäss der entsprechenden Zonenpolicy betrieben werden."
                    ),
                    catalog.BasePart(
                        id="s1_gdn",
                        name="guidance",
                        prose="Unter https://intranet.dti.bk.admin.ch/isb_kp/de/home/ikt-vorgaben/sicherheit/si003-netzwerksicherheit_in_der_bundesverwaltung.html sind die Zonen zusammengestellt. Ein IT-System, das keiner anderen Zone zugeordnet werden kann, gehört zum Internet. In diesem Fall gibt es keine Zonenpolicy. Zudem kann es Netzwerkkomponenten geben, die weder einer Zone noch dem Internet angehören. Diese Komponenten müssen dokumentiert sein."
                    )
                ]
            ),
            catalog.Control(
                id="s2",
                title="Updates und Fehlerkorrekturen",
                parts=[
                    catalog.BasePart(
                        id="s2_stm",
                        name="statement",
                        prose="Für das IT-System muss entweder sichergestellt sein, dass der oder die Hersteller während der ganzen Lebensdauer Updates und Fehlerkorrekturen (Patches) bereitstellen, die zeitnah geprüft und eingespielt werden, oder das IT-System in einer dedizierten und möglichst stark abgeschotteten Zone betrieben wird (z.B. Technik Zone)."
                    ),
                    catalog.BasePart(
                        id="s2_gdn",
                        name="guidance",
                        prose="Für APS, die nicht permanent mit dem Netzwerk verbunden sind, muss sichergestellt sein, dass diese mindestens einmal pro Monat mit Updates und Patches aktualisiert werden. Beim Patchen muss das Zusammenspiel der verschiedenen Typen von Software (auf unterschiedlichen Schichten) mit berücksichtigt werden (z.B. Anwendung, Middleware, Datenbank, Betriebssystem, Virtualisierung, Server, Storage, Netzwerk)."
                    )
                ]
            ),
            catalog.Control(
                id="s3.1",
                title="Dienstkonti",
                parts=[
                    catalog.BasePart(
                        id="s3.1_stm",
                        name="statement",
                        prose="Von Systemdiensten benutzte Konti (Dienstkonti) müssen spezifisch und nur mit den für die Diensterbringung minimal erforderlichen Rechten ausgerüstet sein."
                    ),
                    catalog.BasePart(
                        id="s3.1_gdn",
                        name="guidance",
                        prose="Ein Dienstkonto ist spezifisch, wenn es für nur einen Dienst verwendet wird."
                    )
                ]
            ),
            catalog.Control(
                id="s3.2",
                title="Dienstkonti",
                parts=[
                    catalog.BasePart(
                        id="s3.2_stm",
                        name="statement",
                        prose="Die Dienstkonti müssen automatisiert verwaltet werden und eine kryptografisch starke Authentifikation erfordern. Im Idealfall basiert diese Authentifikation auf dem Einsatz asymmetrischer Kryptografie, wobei die dazu verwendeten privaten Schlüssel sicher hinterlegt werden müssen."
                    ),
                    catalog.BasePart(
                        id="s3.2_gdn",
                        name="guidance",
                        prose="Die Anforderungen an die Authentifikation von Dienstkonti sind höher als bei normalen Konti. Insofern bietet sich hier der Einsatz asymmetrischer Kryptografie an. Beim Einsatz von Passwörtern müssen diese deutlich stärker (und länger) sein als bei der Benutzerauthentifikation."
                    )
                ]
            ),
            catalog.Control(
                id="s4.1",
                title="Integritäts- und Malwareschutz",
                parts=[
                    catalog.BasePart(
                        id="s4.1_stm",
                        name="statement",
                        prose="Die Integrität der auf dem IT-System eingesetzten Softwarekomponenten muss sichergestellt sein (z.B. mit Hilfe von digitalen Signaturen). Insbesondere muss jedes Server-System mit erhöhtem Schutzbedarf regelmässig einer Integritätsprüfung unterzogen werden."
                    ),
                    catalog.BasePart(
                        id="s4.1_gdn",
                        name="guidance",
                        prose="Diese Anforderung ergibt sich u.a. aus dem BRB vom 16. Dezember 2009. Vergleiche dazu auch die Technologiebetrachtung «Integritätsprüfung von Systemen» (https://intranet.ncsc.admin.ch/dam/ncscintra/de/dokumente/technologiebetrachtungen/Technolgiebetrachtung-Integritaetspruefung_von_Systemen_V1-0-d.pdf.download.pdf/Technolgiebetrachtung-Integritaetspruefung_von_Systemen_V1-0-d.pdf)."
                    )
                ]
            ),
            catalog.Control(
                id="s4.2",
                title="Integritäts- und Malwareschutz",
                parts=[
                    catalog.BasePart(
                        id="s4.2_stm",
                        name="statement",
                        prose="Wird ein Integritätsverlust festgestellt, muss das IT-System unmittelbar vom Netzwerk getrennt, gesichert und untersucht werden. Im Falle einer bestätigten Kompromittierung muss das IT-System vollständig gelöscht und neu aufgesetzt werden."
                    ),
                    catalog.BasePart(
                        id="s4.2_gdn",
                        name="guidance",
                        prose="Ein Integritätsverlust deutet auf eine Kompromittierung des IT-Systems hin. Insofern ist dann erforderlich, dass das IT-System unmittelbar vom Netzwerk getrennt, gesichert und untersucht wird, und dass das System im Falle einer bestätigten Kompromittierung vollständig gelöscht und neu aufgesetzt wird."
                    )
                ]
            ),
            catalog.Control(
                id="s4.3",
                title="Integritäts- und Malwareschutz",
                parts=[
                    catalog.BasePart(
                        id="s4.3_stm",
                        name="statement",
                        prose="Das IT-System muss in ein auf [SB003] aufbauendes Malwareschutzkonzept eingebunden sein, das insbesondere auch regelt, wie bei einem Malwarebefall vorzugehen ist und welche Stellen wie informiert werden müssen."
                    ),
                    catalog.BasePart(
                        id="s4.3_gdn",
                        name="guidance",
                        prose="Malwareschutz ist ein wichtiges Thema, das für das IT-System konzeptionell und möglichst umfassend angegangen werden muss. Als Grundlage kann [SB003] verwendet werden."
                    )
                ]
            ),
            catalog.Control(
                id="s5.1",
                title="Bundesclients",
                parts=[
                    catalog.BasePart(
                        id="s5.1_stm",
                        name="statement",
                        prose="Auf dem Bundesclient müssen interne nicht-flüchtige Datenspeicher (z.B. Festplatten) transparent verschlüsselt sein. Für ein MDM-System muss zudem eine Möglichkeit vorgesehen sein, das System entfernt auf seine Grundeinstellungen zurückzusetzen und sämtliche lokal gespeicherten Informationen zu löschen."
                    ),
                    catalog.BasePart(
                        id="s5.1_gdn",
                        name="guidance",
                        prose="Eine Verschlüsselung ist transparent, wenn sie für den Benutzer ohne spezielle Interaktion (automatisch) erfolgt. Die Verschlüsselung von lokal auf Bundesclients (nicht-flüchtig) gespeicherten Daten ist für Bundesclients zwingend. Insofern ist eine Festplattenverschlüsselung (z.B. BitLocker) zu aktivieren."
                    )
                ]
            ),
            catalog.Control(
                id="s5.2",
                title="Bundesclients",
                parts=[
                    catalog.BasePart(
                        id="s5.2_stm",
                        name="statement",
                        prose="Bei fehlender Benutzeraktivität muss der Zugriff auf den Bundesclient automatisch gesperrt werden (auf APS nach maximal 15 Minuten und auf MDM-Systemen nach maximal 3 Minuten). Eine manuelle Aktivierung der Systemzugriffssperre muss ebenfalls möglich sein. Ist eine Sperrung aus technischen Gründen nicht möglich, muss der Zugang zu unbeaufsichtigten aber freigeschalteten Bundesclients physisch geschützt sein (z.B. durch Abschließen des Raumes)."
                    ),
                    catalog.BasePart(
                        id="s5.2_gdn",
                        name="guidance",
                        prose="Es muss sichergestellt sein, dass eine erfolgreich durchgeführte Benutzerauthentifikation nicht von Dritten missbraucht werden kann. Dazu muss ein Bundesclient entweder bei fehlender Benutzeraktivität automatisch gesperrt werden oder der Zugang zum Client physisch geschützt sein. In heiklen Fällen können natürlich auch beide Möglichkeiten kombiniert werden."
                    )
                ]
            ),
            catalog.Control(
                id="s5.3",
                title="Bundesclients",
                parts=[
                    catalog.BasePart(
                        id="s5.3_stm",
                        name="statement",
                        prose="Auf dem Bundesclient darf keine Autorun-Funktion beim Anschluss externer Datenträger (z.B. USB-Sticks) aktiviert sein."
                    ),
                    catalog.BasePart(
                        id="s5.3_gdn",
                        name="guidance",
                        prose="Damit soll verhindert werden, dass durch den Einsatz von nicht kontrollierbaren externen Datenträgern Malware auf ein IT-System eingebracht und ausgeführt werden kann."
                    )
                ]
            ),
            catalog.Control(
                id="s5.4",
                title="Bundesclients",
                parts=[
                    catalog.BasePart(
                        id="s5.4_stm",
                        name="statement",
                        prose="Die Benutzerinnen und Benutzer des APS dürfen über keine lokalen Administratorenrechte verfügen."
                    ),
                    catalog.BasePart(
                        id="s5.4_gdn",
                        name="guidance",
                        prose="Diese Anforderung soll verhindern, dass ein Angriff über kompromittierte Benutzerkonti weitergetragen werden kann."
                    )
                ]
            ),
            catalog.Control(
                id="s5.5",
                title="Bundesclients",
                parts=[
                    catalog.BasePart(
                        id="s5.5_stm",
                        name="statement",
                        prose="Ein administrativer Zugriff zu Supportzwecken auf das APS ist nur mit einer vorgängigen, expliziten Einwilligung der Benutzenden erlaubt."
                    ),
                    catalog.BasePart(
                        id="s5.5_gdn",
                        name="guidance",
                        prose="Diese Anforderung soll verhindern, dass ein administrativer Zugriff auf ein APS ohne Kenntnis der Benutzenden erfolgt."
                    )
                ]
            ),
            catalog.Control(
                id="s6.1",
                title="Peripheriegeräte",
                parts=[
                    catalog.BasePart(
                        id="s6.1_a_stm",
                        name="statement",
                        prose="Das Peripheriegerät darf eingesetzt werden, wenn es durch eine Beschaffungsstelle des Bundes beschafft worden ist."
                    ),
                    catalog.BasePart(
                        id="s6.1_b_stm",
                        name="statement",
                        prose="Das Peripheriegerät darf eingesetzt werden, wenn seine Integrierbarkeit und grundsätzliche Sicherheit vom LE nachweislich bestätigt worden ist."
                    ),
                    catalog.BasePart(
                        id="s6.1_gdn",
                        name="guidance",
                        prose="Mit dieser Anforderung soll sichergestellt werden, dass in der Bundesverwaltung nur kontrollierte Peripheriegeräte eingesetzt werden. Präzisierung zu b): Die Integrierbarkeit bedeutet z.B. auch, dass das Gerät für Funktionen wie ScanToMail an die Mitarbeiterverzeichnisse der Bundesverwaltung angebunden werden kann."
                    )
                ]
            ),
            catalog.Control(
                id="s6.2",
                title="Peripheriegeräte",
                parts=[
                    catalog.BasePart(
                        id="s6.2_stm",
                        name="statement",
                        prose="Das Peripheriegerät muss vom LE minimal konfiguriert und vor nicht berechtigten Änderungen (der Konfiguration) geschützt sein."
                    ),
                    catalog.BasePart(
                        id="s6.2_gdn",
                        name="guidance",
                        prose="Die minimale Konfigurierung und Härtung gelten auch für Peripheriegeräte."
                    )
                ]
            ),
            catalog.Control(
                id="s6.3",
                title="Peripheriegeräte",
                parts=[
                    catalog.BasePart(
                        id="s6.3_a_stm",
                        name="statement",
                        prose="Wird das Gerät zum Drucken klassifizierter Dokumente benutzt, muss das Gerät lokal betrieben werden oder eine Möglichkeit zur Personenauthentifizierung am Gerät bestehen."
                    ),
                    catalog.BasePart(
                        id="s6.3_b_stm",
                        name="statement",
                        prose="Wird das Gerät zum Drucken klassifizierter Dokumente benutzt, müssen interne nicht-flüchtige Datenspeicher (z.B. Festplatten) gemäß einschlägigen Empfehlungen überschrieben werden können, wobei die Überschreibung entweder manuell vom Benutzer oder automatisiert ausgelöst werden kann."
                    ),
                    catalog.BasePart(
                        id="s6.3_gdn",
                        name="guidance",
                        prose="Präzisierung zu b): 'Einschlägige Empfehlungen' sind z.B. DoD 5220.22-M oder NIST SP 800-88."
                    )
                ]
            ),
            catalog.Control(
                id="s6.4",
                title="Peripheriegeräte",
                parts=[
                    catalog.BasePart(
                        id="s6.4_stm",
                        name="statement",
                        prose="Für die Nutzung von privaten Peripheriegeräten beim Mobilen Arbeiten muss die Einsatzrichtlinie [E026] eingehalten werden."
                    ),
                    catalog.BasePart(
                        id="s6.4_gdn",
                        name="guidance",
                        prose="Diese Anforderung regelt indirekt den Einsatz von privaten Peripheriegeräten, insbesondere im Home Office."
                    )
                ]
            )
        ]
    )

    # Construct section A - Anwendungen
    si001_anwendungen = catalog.Group(
        id="anwendungen",
        title="Anwendungen",
        controls=[
            catalog.Control(
                id="a1.1",
                title="Beschaffung / Entwicklung",
                parts=[
                    catalog.BasePart(
                        id="a1.1_stm",
                        name="statement",
                        prose="Die Anwendung muss im Rahmen eines methodischen Vorgehens (vorzugsweise nach HERMES) und unter frühzeitiger Berücksichtigung von einschlägigen Sicherheitsvorgaben und -empfehlungen («Best Practices») beschafft bzw. entwickelt werden."
                    ),
                    catalog.BasePart(
                        id="a1.1_gdn",
                        name="guidance",
                        prose="Weitergehende Informationen zu HERMES finden sich unter https://www.hermes.admin.ch. Für die Entwicklung von Web-Anwendungen sind z.B. die Vorgaben und Empfehlungen der Open Web Application Security Project (OWASP) mit zu berücksichtigen. Diese decken auch die sichere Verwaltung von Programmcode mit ab."
                    )
                ]
            ),
            catalog.Control(
                id="a1.2",
                title="Beschaffung / Entwicklung",
                parts=[
                    catalog.BasePart(
                        id="a1.2_a_stm",
                        name="statement",
                        prose="Bei der Entwicklung der Anwendungssoftware muss insbesondere sichergestellt sein, dass der Quellcode muss sicher aufbewahrt wird."
                    ),
                    catalog.BasePart(
                        id="a1.2_b_stm",
                        name="statement",
                        prose="Bei der Entwicklung der Anwendungssoftware muss insbesondere sichergestellt sein, dass der Zugriff auf die entsprechenden Repositories klar geregelt und nachvollziehbar kontrolliert wird."
                    ),
                    catalog.BasePart(
                        id="a1.2_c_stm",
                        name="statement",
                        prose="Bei der Entwicklung der Anwendungssoftware muss insbesondere sichergestellt sein, dass die Build-Prozesse überwacht werden und Änderungen an der Build-Pipeline nur kontrolliert erfolgen können."
                    ),
                    catalog.BasePart(
                        id="a1.2_d_stm",
                        name="statement",
                        prose="Bei der Entwicklung der Anwendungssoftware muss insbesondere sichergestellt sein, dass die Software regelmäßig getestet wird."
                    ),
                    catalog.BasePart(
                        id="a1.2_e_stm",
                        name="statement",
                        prose="Bei der Entwicklung der Anwendungssoftware muss insbesondere sichergestellt sein, dass die Integrität der Software jederzeit sichergestellt ist (z.B. mit Hilfe von digitalen Signaturen)."
                    ),
                    catalog.BasePart(
                        id="a1.2_gdn",
                        name="guidance",
                        prose="Diese Anforderung betrifft den Entwicklungsprozess der Anwendungssoftware und den entsprechenden «Best Practices». Für die agile Softwareentwicklung im Rahmen des SAFe-Modells sollen die Sicherheitsanforderungen als Definition of Done auf Stufe des Produkts eingepflegt werden. Die Sicherheitsdokumente sollen für jedes Product Increment aktualisiert werden und sind einzeln als Akzeptanzkriterien aufzuführen."
                    )
                ]
            ),
            catalog.Control(
                id="a2",
                title="Wartung und Pflege",
                parts=[
                    catalog.BasePart(
                        id="a2_stm",
                        name="statement",
                        prose="Für die Anwendung und ihre Komponenten (z.B. Software-Bibliotheken) müssen während der ganzen Lebensdauer eine professionelle Wartung und Pflege sichergestellt sein. Darunter fallen insbesondere auch die Einspielung von regelmäßigen und betrieblich oder sicherheitstechnisch notwendigen Updates und Fehlerkorrekturen (Patches)."
                    ),
                    catalog.BasePart(
                        id="a2_gdn",
                        name="guidance",
                        prose="Wartung und Pflege sind auch für Anwendungssoftware (und alle verwendeten Software-Bibliotheken) wichtige Themen. Die Einhaltung professioneller Vorgehensweisen und Prozesse ist wichtig. Die Abhängigkeiten zu weiteren Software-Bibliotheken und die davon resultierenden Schwachstellen kann z.B. mit dem Tool «OWASP Dependency-Check» überprüft werden (https://owasp.org/www-project-dependency-check)."
                    )
                ]
            )
        ]
    )

    # Construct section Z - Zonen
    si001_zonen = catalog.Group(
        id="zonen",
        title="Zonen",
        controls=[
            catalog.Control(
                id="z1.1",
                title="Konformität",
                parts=[
                    catalog.BasePart(
                        id="z1.1_stm",
                        name="statement",
                        prose="Die Zone muss konform zum Zonenmodell Bund sein und über einen Inhaber, einen eindeutigen Namen, eine Zonenpolicy und einen Betreiber verfügen (gilt nicht für das Internet bzw. die Zone Internet). Umfasst die Zone IT-Systeme und Anwendungen, die ausserhalb der Bundesverwaltung (z.B. in einer Public Cloud) betrieben werden, dann muss die netzwerkmässige Erschliessung in der Zonenpolicy beschrieben sein."
                    ),
                    catalog.BasePart(
                        id="z1.1_gdn",
                        name="guidance",
                        prose="Die Eindeutigkeit kann z.B. dadurch erreicht werden, dass der Inhaber als Suffix dem Namen angehängt wird (z.B. SZ-FUB für eine von der FUB betriebene Server Zone). Falls ein Inhaber eine Zone mehrfach umsetzen lässt, müssen die entsprechenden Namen unterscheidbar sein. Der Betreiber ist ein LE, der die Zone im Auftrag des Inhabers netzwerktechnisch betreibt. Falls der Inhaber der Zone ein LE ist, können der Inhaber und der Betreiber auch identisch sein. Falls der Inhaber einer (Unter-)Zone die Policy ändert, muss dem Betreiber eine angemessene Frist für die Umsetzung eingeräumt werden."
                    )
                ]
            ),
            catalog.Control(
                id="z1.2",
                title="Konformität",
                parts=[
                    catalog.BasePart(
                        id="z1.2_stm",
                        name="statement",
                        prose="Der Betreiber muss sicherstellen, dass nur gemäss Zonenpolicy zulässige Kommunikation von und zu der Zone stattfinden kann, und dass mit Hilfe geeigneter komplementärer Sicherheitsmassnahmen (z.B. Isolierung und Segmentierung) von dieser Kommunikation keine zusätzlichen Bedrohungen und Risiken für andere IT-Systeme und Anwendungen in- und ausserhalb der Zone ausgeht."
                    ),
                    catalog.BasePart(
                        id="z1.2_gdn",
                        name="guidance",
                        prose="Die Zonenpolicy stellt das Regelwerk für Zugriffe in und aus der Zone dar, und der Betreiber hat sicherzustellen, dass die Policy sinnvoll umgesetzt ist. Die Umsetzung ist mit dem Zoneninhaber abzusprechen. Das gilt namentlich auch für kurzfristige Abweichungen von der Policy, falls diese betrieblich erforderlich sind."
                    )
                ]
            ),
            catalog.Control(
                id="z1.3",
                title="Konformität",
                parts=[
                    catalog.BasePart(
                        id="z1.3_stm",
                        name="statement",
                        prose="Die Zone muss in das Verzeichnis integriert sein, das vom zuständigen ISBD geführt und dem NCSC zur Verfügung gestellt wird. Ein ISBD ist zuständig, wenn eine Verwaltungseinheit des Departementes entweder als Inhaber oder Betreiber der Zone auftritt."
                    ),
                    catalog.BasePart(
                        id="z1.3_gdn",
                        name="guidance",
                        prose="Diese Anforderung ist erforderlich, damit eine Übersicht über die in der Bundesverwaltung betriebenen Zonen erstellt werden kann. Aufgrund der definierten Zuständigkeiten kann eine Zone auch doppelt geführt sein (einmal aus der Sicht des Inhabers und einmal aus der Sicht des Betreibers)."
                    )
                ]
            ),
            catalog.Control(
                id="z2.1",
                title="Zugriffe",
                parts=[
                    catalog.BasePart(
                        id="z2.1_a_stm",
                        name="statement",
                        prose="Ein eingeschränkter Zugriff in die Zone ist nur für Personen und automatisierte Prozesse zulässig, die mit einem Authentifikations- und Identitätsnachweismittel mindestens der Stufe «mittel» authentifiziert worden sind (für Messgeräte reicht die Stufe «tief»). Die folgenden Ausnahmen sind erlaubt: Anonyme und personalisierte Zugriffe im Rahmen von E-Government-Anwendungen, die einer breiten Bevölkerungsschicht in einer SZ zugänglich gemacht werden. Die entsprechenden Webseiten müssen mit TLS (HTTPS) abgesichert und Formulare vor automatisierten Angriffen geschützt werden (z.B. mit Hilfe von CAPTCHAs). "
                    ),
                    catalog.BasePart(
                        id="z2.1_b_stm",
                        name="statement",
                        prose="Ein eingeschränkter Zugriff in die Zone ist nur für Personen und automatisierte Prozesse zulässig, die mit einem Authentifikations- und Identitätsnachweismittel mindestens der Stufe «mittel» authentifiziert worden sind (für Messgeräte reicht die Stufe «tief»). Die folgenden Ausnahmen sind erlaubt: Zeitlich befristete Zugriffe zum Hochladen von Daten auf ein Server-System."
                    ),
                    catalog.BasePart(
                        id="z2.1_c_stm",
                        name="statement",
                        prose="Ein eingeschränkter Zugriff in die Zone ist nur für Personen und automatisierte Prozesse zulässig, die mit einem Authentifikations- und Identitätsnachweismittel mindestens der Stufe «mittel» authentifiziert worden sind (für Messgeräte reicht die Stufe «tief»). Die folgenden Ausnahmen sind erlaubt: Automatisierte und im Einverständnis mit dem Zoneninhaber durchgeführte Zugriffe im Rahmen von Sicherheitsüberprüfungen von Web-Auftritten (Scans)."
                    ),
                    catalog.BasePart(
                        id="z2.1_d_stm",
                        name="statement",
                        prose="Ein eingeschränkter Zugriff in die Zone ist nur für Personen und automatisierte Prozesse zulässig, die mit einem Authentifikations- und Identitätsnachweismittel mindestens der Stufe «mittel» authentifiziert worden sind (für Messgeräte reicht die Stufe «tief»). Erfolgt der Zugriff in eine Zone mit erhöhtem Schutzbedarf (z.B. SZ+) muss das Authentifikations- und Identitätsnachweismittel mindestens der Stufe «hoch» gemäss Anhang B sein und die oben aufgeführten Ausnahmen a) und b) sind dann nicht zulässig."
                    ),
                    catalog.BasePart(
                        id="z2.1_gdn",
                        name="guidance",
                        prose="Ein Zugriff ist eingeschränkt, wenn er mit Hilfe technischer Vorkehrungen (z.B. IP-Paketfilterung) auf ein oder ein paar wenige definierte IT-Systeme oder Anwendungen und auf die für den Zugriff zwingend erforderlichen Protokolle eingeschränkt ist. Anderenfalls heisst der Zugriff uneingeschränkt."
                    )
                ]
            ),
            catalog.Control(
                id="z2.2",
                title="Zugriffe",
                parts=[
                    catalog.BasePart(
                        id="z2.2_stm",
                        name="statement",
                        prose="Ein uneingeschränkter Zugriff in die Zone ist nur für Personen zulässig, die sich über einen Bundesclient verbinden, mit einem Authentifikations- und Identitätsnachweismittel mindestens der Stufe «hoch» gemäss Anhang B authentifiziert sind und die Verbindung kryptografisch abgesichert ist (z.B. mit Hilfe von SSH)."
                    ),
                    catalog.BasePart(
                        id="z2.2_gdn",
                        name="guidance",
                        prose="Uneingeschränkte Zonenzugriffe sind grundsätzlich zu vermeiden bzw. sollen nur für bestimmte Use Cases (z.B. Administration) zugelassen sein. In diesem Fall sind erhöhte Anforderungen an die zugreifenden Geräte und die Kommunikationssicherheit zu stellen."
                    )
                ]
            ),
            catalog.Control(
                id="z3",
                title="Zonenübergreifende Kommunikation",
                parts=[
                    catalog.BasePart(
                        id="z3_stm",
                        name="statement",
                        prose="Jede zonenübergreifende Kommunikation muss über eine PEZ erfolgen. Diese hat sicherzustellen, dass die Kommunikation konform zu den betroffenen Zonenpolicies ist. Dazu müssen die erlaubten Kommunikationsmuster und -beziehungen in den Policies so präzis wie möglich (idealerweise auf der Anwendungsschicht und in Form einer «Allow List») spezifiziert sein."
                    ),
                    catalog.BasePart(
                        id="z3_gdn",
                        name="guidance",
                        prose="Obwohl der erste Satz grundsätzlich auch für die Kommunikation von einer Unterzone in die darüber liegende Zone gilt, kann in begründeten und in den Policies der entsprechenden Unterzonen dokumentierten Fällen darauf verzichtet werden. Allerdings sind dann auch erhöhte Anforderungen an die zugreifenden IT-Systeme, die Kommunikationssicherheit und die Aufzeichnung der Kommunikationsbeziehungen zu stellen."
                    )
                ]
            ),
            catalog.Control(
                id="z4.1",
                title="PEZ",
                parts=[
                    catalog.BasePart(
                        id="z4.1_stm",
                        name="statement",
                        prose="Die in einer PEZ betriebenen PEPs dürfen nur zonenintern virtualisiert betrieben werden, d.h. auf der gemeinsam genutzten Hardware dürfen keine IT-Systeme aus anderen Zonen betrieben werden."
                    ),
                    catalog.BasePart(
                        id="z4.1_gdn",
                        name="guidance",
                        prose="Diese Anforderung stellt sicher, dass die Virtualisierung innerhalb einer PEZ auf zoneninterne IT-Systeme beschränkt bleibt, um Sicherheitsrisiken durch Vermischung von Zonen zu vermeiden."
                    )
                ]
            ),
            catalog.Control(
                id="z4.2",
                title="PEZ",
                parts=[
                    catalog.BasePart(
                        id="z4.2_stm",
                        name="statement",
                        prose="Der Inhaber einer PEZ bzw. einer Web-Proxy-Infrastruktur muss regeln, wie der Zugriff auf Ressourcen im Internet erfolgt und welche Zugriffe zulässig sind. Diese Regelung kann entweder in der Zonenpolicy der PEZ oder in einer separaten Vorgabe erfolgen. Das NCSC kann Einträge in den entsprechenden Regelsätzen erlassen."
                    ),
                    catalog.BasePart(
                        id="z4.2_gdn",
                        name="guidance",
                        prose="Für die Regelung der zulässigen Zugriffe auf Ressourcen im Internet ist der Inhaber einer PEZ bzw. einer in einer PEZ betriebenen Web-Proxy-Infrastruktur zuständig. Dabei muss es möglich sein, dass das NCSC vor dem Hintergrund aktuell beobachteter Angriffsvektoren Einträge in den entsprechenden Regelsätzen erlässt."
                    )
                ]
            ),
            catalog.Control(
                id="z4.3",
                title="PEZ",
                parts=[
                    catalog.BasePart(
                        id="z4.3_stm",
                        name="statement",
                        prose="Die Anbindung einer PEZ an das Internet muss hochverfügbar und allenfalls redundant ausgelegt sein. Darüber hinaus muss der Betreiber mit Hilfe geeigneter Massnahmen sicherstellen, dass die durch die PEZ vom Internet getrennten IT-Systeme adäquat vor (D)DoS-Angriffen geschützt sind."
                    ),
                    catalog.BasePart(
                        id="z4.3_gdn",
                        name="guidance",
                        prose="(D)DoS-Angriffe stellen ein zunehmend grosses Problem dar. Um sich vor solchen Angriffen wirksam zu schützen, muss die Anbindung der PEZ an das Internet hochverfügbar und allenfalls redundant ausgelegt sein."
                    )
                ]
            ),
            catalog.Control(
                id="z5.1",
                title="Überwachung",
                parts=[
                    catalog.BasePart(
                        id="z5.1_stm",
                        name="statement",
                        prose="Innerhalb einer Zone muss die Kommunikation dahingehend überwacht werden, dass Angriffe möglichst zuverlässig erkannt werden können (z.B. mit Hilfe von IDS/IPS) und der Betreiber im Bedarfsfall zeitnah und adäquat reagieren kann."
                    ),
                    catalog.BasePart(
                        id="z5.1_gdn",
                        name="guidance",
                        prose="Weil die Überwachung einer Zone im Hinblick auf Angriffe sinnvollerweise automatisiert erfolgt, wird der Einsatz von IDS/IPS postuliert. Das ist aber nicht als Zwang zu verstehen. Falls es andere Möglichkeiten gibt, Angriffe zeitnah zu erkennen und adäquat zu reagieren, dann sind diese natürlich auch möglich."
                    )
                ]
            ),
            catalog.Control(
                id="z5.2",
                title="Überwachung",
                parts=[
                    catalog.BasePart(
                        id="z5.2_stm",
                        name="statement",
                        prose="Die bei der Überwachung anfallenden Informationen müssen gemäss den rechtlichen Vorgaben (insbesondere Datenschutzgesetzgebung und «Verordnung über die Bearbeitung von Personendaten, die bei der Nutzung der elektronischen Infrastruktur des Bundes anfallen» vom 22. Februar 2012) aufbewahrt und vor nachträglichen Manipulationen geschützt werden. Im Bedarfsfall müssen die Informationen dem NCSC zur Verfügung gestellt werden."
                    ),
                    catalog.BasePart(
                        id="z5.2_gdn",
                        name="guidance",
                        prose="Die hier erwähnten rechtlichen Vorgaben sind nicht abschliessend zu betrachten, d.h. es können durchaus noch andere Vorgaben existieren, die im Rahmen der Überwachung im Sinne dieser Anforderung mit berücksichtigt werden müssen."
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