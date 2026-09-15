"""
Regulatorisk Modul
==================
Kartlägger och bedömer efterlevnad av NIS2, DORA, GDPR och nationella krav

Del av: NEAB Security Assessment Suite
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class Regelverk(Enum):
    """Relevanta regelverk för energisektorn"""
    NIS2 = "NIS2"
    DORA = "DORA"
    GDPR = "GDPR"
    CER = "CER"
    NATIONELL_ENERGI = "Nationell energireglering"


class EfterlEvnadStatus(Enum):
    """Status för regelverksefterlevnad"""
    UPPFYLLT = "Uppfyllt"
    DELVIS = "Delvis uppfyllt"
    EJ_UPPFYLLT = "Ej uppfyllt"
    INTE_TILLAMPLIGT = "Inte tillämpligt"


@dataclass
class RegulatorisktKrav:
    """Representerar ett enskilt regulatoriskt krav"""
    regelverk: str
    artikel: str
    krav_beskrivning: str
    tillampning: str
    status: str
    bevis: Optional[str] = None
    gap_analys: Optional[str] = None
    föreslagen_åtgärd: Optional[str] = None
    ansvarig: Optional[str] = None
    deadline: Optional[str] = None
    koppling_cis: List[str] = field(default_factory=list)


class RegulatoriskAnalys:
    """
    Hanterar regulatorisk kartläggning och gap-analys
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.organisation = config.get("organisation", {})

        # Ladda regulatoriska krav från databas/config
        self.nis2_krav = self._ladda_nis2_krav()
        self.dora_krav = self._ladda_dora_krav()
        self.gdpr_krav = self._ladda_gdpr_krav()
        self.cer_krav = self._ladda_cer_krav()
        self.nationella_krav = self._ladda_nationella_krav()

        logger.info("Regulatorisk modul initierad")

    def _ladda_nis2_krav(self) -> List[Dict]:
        """Laddar NIS2-krav relevanta för energisektorn"""
        return [
            {
                "artikel": "Art. 21",
                "krav": "Cybersäkerhetsriskhanteringsåtgärder",
                "beskrivning": "Organisationen ska ha riskhanteringsåtgärder för nät och informationssystem",
                "applicerbarhet": "Väsentlig enhet inom energisektorn",
                "specifika_krav": [
                    "Riskanalysmetodik",
                    "Incident hantering",
                    "Kontinuitetsplanering",
                    "Säkerhet i leveranskedjan",
                    "Säkerhetsåtgärder vid förvärv, utveckling och underhåll",
                    "Utbildning av personal",
                    "Kryptografi och kryptering",
                    "Personalsäkerhet",
                    "Åtkomstkontroll",
                    "Asset management"
                ],
                "cis_controls": ["CIS 1", "CIS 4", "CIS 5", "CIS 6", "CIS 7", "CIS 8"]
            },
            {
                "artikel": "Art. 23",
                "krav": "Rapporteringsskyldigheter",
                "beskrivning": "Väsentliga och viktiga enheter ska rapportera betydande incidenter",
                "specifika_krav": [
                    "Tidig varning (24h)",
                    "Incidentanmälan (72h)",
                    "Slutrapport",
                    "Frivillig rapportering av hot"
                ],
                "cis_controls": ["CIS 17"]
            },
            {
                "artikel": "Art. 24",
                "krav": "Användning av europeiska cybersäkerhetscertifikat",
                "beskrivning": "Möjlighet att använda certifikat för att visa efterlevnad",
                "cis_controls": ["CIS 18"]
            },
            {
                "artikel": "Art. 20",
                "krav": "Styrning och ledningsansvar",
                "beskrivning": "Styrelsen och VD ansvarar för implementering och övervakning",
                "specifika_krav": [
                    "Godkänna riskhanteringsåtgärder",
                    "Genomgå utbildning",
                    "Bära ansvaret för brister"
                ],
                "cis_controls": ["CIS 1"]
            }
        ]

    def _ladda_dora_krav(self) -> List[Dict]:
        """
        Laddar DORA-krav (Digital Operational Resilience Act)
        OBS: DORA gäller främst finanssektorn, men kan vara relevant för
        betalningsintegration och kundtjänster
        """
        return [
            {
                "artikel": "Kap. II",
                "krav": "IKT-riskhantering",
                "beskrivning": "Ramverk för hantering av IKT-risker",
                "tillamplig_for_neab": "Begränsad - endast betalningssystem",
                "cis_controls": ["CIS 4", "CIS 5"]
            },
            {
                "artikel": "Kap. III",
                "krav": "IKT-relaterad incidenthantering",
                "beskrivning": "Hantering och rapportering av IKT-incidenter",
                "tillamplig_for_neab": "Delvis - för kundbetalningar",
                "cis_controls": ["CIS 17"]
            }
        ]

    def _ladda_gdpr_krav(self) -> List[Dict]:
        """Laddar GDPR-krav relevanta för energibolag"""
        return [
            {
                "artikel": "Art. 5",
                "krav": "Principer för behandling av personuppgifter",
                "beskrivning": "Laglighet, ändamålsbegränsning, dataminimering, korrekthet",
                "tillampning_neab": "Kund- och mätdata, personaluppgifter",
                "cis_controls": ["CIS 3", "CIS 13"]
            },
            {
                "artikel": "Art. 32",
                "krav": "Säkerhet för behandling",
                "beskrivning": "Lämpliga tekniska och organisatoriska åtgärder",
                "specifika_krav": [
                    "Pseudonymisering och kryptering",
                    "Förmåga att säkerställa konfidentialitet",
                    "Förmåga att återställa tillgänglighet",
                    "Process för regelbunden testning"
                ],
                "tillampning_neab": "Alla system som hanterar PII",
                "cis_controls": ["CIS 3", "CIS 8", "CIS 10", "CIS 11"]
            },
            {
                "artikel": "Art. 33",
                "krav": "Anmälan av personuppgiftsincident",
                "beskrivning": "Anmälan till tillsynsmyndighet inom 72h",
                "tillampning_neab": "Vid dataintrång i kund-/personalsystem",
                "cis_controls": ["CIS 17"]
            },
            {
                "artikel": "Art. 35",
                "krav": "Konsekvensbedömning avseende dataskydd",
                "beskrivning": "DPIA vid högrisig behandling",
                "tillampning_neab": "AMI/mätdata, profilering av kunder",
                "cis_controls": ["CIS 4"]
            }
        ]

    def _ladda_cer_krav(self) -> List[Dict]:
        """Laddar CER-krav (Critical Entities Resilience)"""
        return [
            {
                "artikel": "Kap. II",
                "krav": "Resiliens för kritiska enheter",
                "beskrivning": "Fysisk säkerhet och motståndskraft mot fysiska hot",
                "tillampning_neab": "Driftcentral, nätstationer, datacenter",
                "cis_controls": ["CIS 1", "CIS 4"]
            }
        ]

    def _ladda_nationella_krav(self) -> List[Dict]:
        """Laddar svenska branschspecifika krav"""
        return [
            {
                "källa": "Ellag (1997:857)",
                "krav": "Leveranssäkerhet",
                "beskrivning": "Säker elförsörjning, undvika driftstörningar",
                "mätetal": "SAIDI/SAIFI-värden, avbrottsstatistik",
                "cis_controls": ["CIS 4", "CIS 11", "CIS 12"]
            },
            {
                "källa": "EIFS 2013:1 (Ei Föreskrifter)",
                "krav": "Rapportering av elavbrott",
                "beskrivning": "Rapportering till Energimarknadsinspektionen",
                "cis_controls": ["CIS 17"]
            },
            {
                "källa": "MSB Föreskrifter (MSBFS 2016:1)",
                "krav": "Samhällsviktig verksamhet",
                "beskrivning": "Riskanalys, kontinuitetsplanering, säkerhetsåtgärder",
                "cis_controls": ["CIS 4", "CIS 5", "CIS 11"]
            }
        ]

    def kartlägg_krav(self, input_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Genomför komplett regulatorisk kartläggning

        Args:
            input_data: Data från formulär eller API

        Returns:
            Dictionary med alla regulatoriska krav och status
        """
        logger.info("Startar regulatorisk kartläggning...")

        krav_lista = []

        # Kartlägg NIS2
        for nis2_krav in self.nis2_krav:
            status = self._bedöm_nis2_status(nis2_krav, input_data)
            krav_lista.append(
                RegulatorisktKrav(
                    regelverk="NIS2",
                    artikel=nis2_krav["artikel"],
                    krav_beskrivning=nis2_krav["krav"],
                    tillampning=nis2_krav.get("applicerbarhet", "Tillämpligt"),
                    status=status,
                    gap_analys=self._generera_gap_analys("NIS2", nis2_krav, status),
                    föreslagen_åtgärd=self._föreslå_åtgärd("NIS2", nis2_krav, status),
                    koppling_cis=nis2_krav.get("cis_controls", [])
                )
            )

        # Kartlägg GDPR
        for gdpr_krav in self.gdpr_krav:
            status = self._bedöm_gdpr_status(gdpr_krav, input_data)
            krav_lista.append(
                RegulatorisktKrav(
                    regelverk="GDPR",
                    artikel=gdpr_krav["artikel"],
                    krav_beskrivning=gdpr_krav["krav"],
                    tillampning=gdpr_krav.get("tillampning_neab", "Tillämpligt"),
                    status=status,
                    gap_analys=self._generera_gap_analys("GDPR", gdpr_krav, status),
                    föreslagen_åtgärd=self._föreslå_åtgärd("GDPR", gdpr_krav, status),
                    koppling_cis=gdpr_krav.get("cis_controls", [])
                )
            )

        # Kartlägg CER
        for cer_krav in self.cer_krav:
            status = self._bedöm_cer_status(cer_krav, input_data)
            krav_lista.append(
                RegulatorisktKrav(
                    regelverk="CER",
                    artikel=cer_krav["artikel"],
                    krav_beskrivning=cer_krav["krav"],
                    tillampning=cer_krav.get("tillampning_neab", "Tillämpligt"),
                    status=status,
                    gap_analys=self._generera_gap_analys("CER", cer_krav, status),
                    föreslagen_åtgärd=self._föreslå_åtgärd("CER", cer_krav, status),
                    koppling_cis=cer_krav.get("cis_controls", [])
                )
            )

        # Sammanställ statistik
        statistik = self._beräkna_statistik(krav_lista)

        resultat = {
            "krav": [self._krav_till_dict(k) for k in krav_lista],
            "statistik": statistik,
            "sammanfattning": self._generera_sammanfattning(statistik),
            "prioriterade_åtgärder": self._identifiera_prioriterade_åtgärder(krav_lista)
        }

        logger.info(f"Kartläggning klar: {len(krav_lista)} krav analyserade")
        return resultat

    def _bedöm_nis2_status(self, krav: Dict, input_data: Optional[Dict]) -> str:
        """Bedömer NIS2-efterlevnad baserat på input"""
        # I produktion: faktisk bedömning baserad på input_data
        # För nu: simulerad bedömning

        if input_data and "nis2_status" in input_data:
            return input_data["nis2_status"].get(krav["artikel"], EfterlEvnadStatus.DELVIS.value)

        # Standardbedömning för NEAB
        if krav["artikel"] == "Art. 21":
            return EfterlEvnadStatus.DELVIS.value  # Riskhantering finns, men behöver förbättras
        elif krav["artikel"] == "Art. 23":
            return EfterlEvnadStatus.DELVIS.value  # Incidenthantering finns, rapportering ej testad
        elif krav["artikel"] == "Art. 20":
            return EfterlEvnadStatus.DELVIS.value  # Styrelseutbildning behövs
        else:
            return EfterlEvnadStatus.DELVIS.value

    def _bedöm_gdpr_status(self, krav: Dict, input_data: Optional[Dict]) -> str:
        """Bedömer GDPR-efterlevnad"""
        if input_data and "gdpr_status" in input_data:
            return input_data["gdpr_status"].get(krav["artikel"], EfterlEvnadStatus.DELVIS.value)

        # Standardbedömning
        if krav["artikel"] == "Art. 32":
            return EfterlEvnadStatus.DELVIS.value  # Säkerhet finns, kryptering delvis
        elif krav["artikel"] == "Art. 35":
            return EfterlEvnadStatus.EJ_UPPFYLLT.value  # DPIA ej genomförd för AMI
        else:
            return EfterlEvnadStatus.UPPFYLLT.value

    def _bedöm_cer_status(self, krav: Dict, input_data: Optional[Dict]) -> str:
        """Bedömer CER-efterlevnad"""
        return EfterlEvnadStatus.DELVIS.value  # Fysisk säkerhet finns, men behöver dokumentation

    def _generera_gap_analys(self, regelverk: str, krav: Dict, status: str) -> str:
        """Genererar gap-analys för ett krav"""
        if status == EfterlEvnadStatus.UPPFYLLT.value:
            return "Kravet uppfylls. Fortsatt övervakning krävs."

        gaps = {
            "NIS2": {
                "Art. 21": "Riskanalys genomförs ad hoc. Saknas formaliserad årlig process och dokumenterad metodik.",
                "Art. 23": "Incidenthanteringsprocess finns men rapporteringsrutiner till myndighet är ej testade.",
                "Art. 20": "Styrelseutbildning i cybersäkerhet saknas."
            },
            "GDPR": {
                "Art. 32": "Kryptering saknas för vissa PII-databaser. MFA ej genomgående.",
                "Art. 35": "DPIA ej genomförd för AMI/mätvärdesbehandling trots högrisig behandling."
            }
        }

        return gaps.get(regelverk, {}).get(krav.get("artikel", ""),
                                           "Gap-analys krävs för detta krav.")

    def _föreslå_åtgärd(self, regelverk: str, krav: Dict, status: str) -> str:
        """Föreslår åtgärd för att uppfylla krav"""
        if status == EfterlEvnadStatus.UPPFYLLT.value:
            return "Upprätthåll nuvarande nivå genom regelbunden översyn."

        åtgärder = {
            "NIS2": {
                "Art. 21": "Implementera formaliserad årlig riskanalysprocess enligt MSB:s metodstöd. Inför gemensam riskpolicy.",
                "Art. 23": "Genomför tabletop-övning av incidentrapportering. Upprätta mallar för rapportering till myndighet.",
                "Art. 20": "Boka styrelseutbildning i cybersäkerhet. Implementera kvartalsvis rapportering till styrelse."
            },
            "GDPR": {
                "Art. 32": "Implementera kryptering för PII-databaser. Utöka MFA till alla system med personuppgifter.",
                "Art. 35": "Genomför DPIA för AMI-system. Dokumentera integritetsskyddsåtgärder."
            },
            "CER": {
                "Kap. II": "Dokumentera fysiska säkerhetsåtgärder. Genomför sårbarhetsbedömning av kritiska anläggningar."
            }
        }

        return åtgärder.get(regelverk, {}).get(krav.get("artikel", ""),
                                               "Utred krav och ta fram åtgärdsplan.")

    def _krav_till_dict(self, krav: RegulatorisktKrav) -> Dict:
        """Konverterar RegulatorisktKrav till dictionary"""
        return {
            "Regelverk": krav.regelverk,
            "Artikel": krav.artikel,
            "Krav": krav.krav_beskrivning,
            "Tillämpning": krav.tillampning,
            "Status": krav.status,
            "Gap-analys": krav.gap_analys,
            "Föreslagen åtgärd": krav.föreslagen_åtgärd,
            "CIS Controls": ", ".join(krav.koppling_cis)
        }

    def _beräkna_statistik(self, krav_lista: List[RegulatorisktKrav]) -> Dict:
        """Beräknar statistik över efterlevnad"""
        total = len(krav_lista)
        uppfyllt = sum(1 for k in krav_lista if k.status == EfterlEvnadStatus.UPPFYLLT.value)
        delvis = sum(1 for k in krav_lista if k.status == EfterlEvnadStatus.DELVIS.value)
        ej_uppfyllt = sum(1 for k in krav_lista if k.status == EfterlEvnadStatus.EJ_UPPFYLLT.value)

        return {
            "totalt_antal_krav": total,
            "uppfyllt": uppfyllt,
            "delvis_uppfyllt": delvis,
            "ej_uppfyllt": ej_uppfyllt,
            "uppfyllnadsgrad_procent": round((uppfyllt + delvis * 0.5) / total * 100, 1) if total > 0 else 0
        }

    def _generera_sammanfattning(self, statistik: Dict) -> str:
        """Genererar textsammanfattning för ledningen"""
        procent = statistik["uppfyllnadsgrad_procent"]

        if procent >= 80:
            nivå = "god"
        elif procent >= 60:
            nivå = "acceptabel"
        else:
            nivå = "otillräcklig"

        return f"""
Nordlunda Energi AB har en {nivå} efterlevnadsnivå ({procent}%) av tillämpliga regelverk.

Av {statistik['totalt_antal_krav']} identifierade krav:
- {statistik['uppfyllt']} fullt uppfyllda
- {statistik['delvis_uppfyllt']} delvis uppfyllda  
- {statistik['ej_uppfyllt']} ej uppfyllda

Prioriterade områden för förbättring: Styrelseutbildning (NIS2), DPIA för mätdata (GDPR), 
samt formalisering av riskhanteringsprocesser.
        """.strip()

    def _identifiera_prioriterade_åtgärder(self, krav_lista: List[RegulatorisktKrav]) -> List[Dict]:
        """Identifierar de mest kritiska åtgärderna"""
        prioriterade = []

        for krav in krav_lista:
            if krav.status == EfterlEvnadStatus.EJ_UPPFYLLT.value:
                prioritet = "Hög"
            elif krav.status == EfterlEvnadStatus.DELVIS.value:
                prioritet = "Medel"
            else:
                continue

            prioriterade.append({
                "regelverk": krav.regelverk,
                "artikel": krav.artikel,
                "krav": krav.krav_beskrivning,
                "prioritet": prioritet,
                "åtgärd": krav.föreslagen_åtgärd
            })

        # Sortera: Hög prioritet först
        prioriterade.sort(key=lambda x: 0 if x["prioritet"] == "Hög" else 1)

        return prioriterade[:10]  # Top 10