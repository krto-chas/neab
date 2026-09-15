"""
Risk Workshop Modul
===================
Genomför strukturerad riskanalys enligt MSB:s metodstöd med STRIDE och CIA-triaden

Del av: NEAB Security Assessment Suite
Baserad på: OT_SecuritySuite_MasterUnifiedPlatform.py (Stoffe, 2024)
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HotKategori(Enum):
    """STRIDE-kategorier för hotmodellering"""
    SPOOFING = "Spoofing (Förfalskning)"
    TAMPERING = "Tampering (Manipulering)"
    REPUDIATION = "Repudiation (Förnekande)"
    INFORMATION_DISCLOSURE = "Information Disclosure (Informationsläckage)"
    DENIAL_OF_SERVICE = "Denial of Service (Överbelastning)"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege (Privilegieeskalering)"


class CIAAspekt(Enum):
    """CIA-triaden för konsekvensanalys"""
    CONFIDENTIALITY = "Konfidentialitet"
    INTEGRITY = "Integritet"
    AVAILABILITY = "Tillgänglighet"


class Sannolikhet(Enum):
    """Sannolikhetsnivåer enligt MSB"""
    LAG = 1
    MEDEL = 2
    HOG = 3
    MYCKET_HOG = 4


class Konsekvens(Enum):
    """Konsekvensnivåer enligt MSB"""
    OBETYDLIG = 1
    MINDRE = 2
    MAATTLIG = 3
    ALLVARLIG = 4
    KATASTROF = 5


@dataclass
class Tillgang:
    """Representerar en tillgång/asset"""
    id: str
    namn: str
    beskrivning: str
    typ: str  # SCADA, IT-system, Data, Process
    kritikalitet: str  # Låg, Medel, Hög, Kritisk
    ägare: str
    beroenden: List[str] = field(default_factory=list)
    rto: Optional[str] = None
    rpo: Optional[str] = None
    klassning: str = "Skyddsvärd"


@dataclass
class Risk:
    """Representerar en identifierad risk"""
    id: str
    tillgang_id: str
    tillgang_namn: str
    hot_beskrivning: str
    hot_kategori: str  # STRIDE
    sarbarhet: str
    konsekvens_beskrivning: str
    konsekvens_cia: List[str]  # C, I, A
    konsekvens_niva: int  # 1-5
    sannolikhet_niva: int  # 1-4
    riskvarde: int  # konsekvens * sannolikhet
    riskniva: str  # Låg, Medel, Hög, Mycket hög
    befintliga_kontroller: List[str] = field(default_factory=list)
    koppling_regelverk: List[str] = field(default_factory=list)
    kommentar: str = ""


@dataclass
class Atgard:
    """Representerar en riskmitigerande åtgärd"""
    id: str
    risk_id: str
    beskrivning: str
    strategi: str  # Reducera, Acceptera, Överföra, Undvika
    cis_controls: List[str]
    ansvarig_roll: str
    planerat_datum: str
    kostnad: str  # L, M, H
    effekt: str  # L, M, H
    status: str = "Planerad"
    kvarvarande_risk: str = "Medel"
    implementation_steg: List[str] = field(default_factory=list)


class RiskWorkshop:
    """
    Hanterar riskworkshop enligt MSB:s metodstöd
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.organisation = config.get("organisation", {})

        # Ladda kritiska tillgångar från config
        self.tillgangar = self._definiera_tillgangar()

        # Känd hotbild för energisektorn
        self.typiska_hot = self._ladda_typisk_hotbild()

        logger.info("Risk Workshop-modul initierad")

    def _definiera_tillgangar(self) -> List[Tillgang]:
        """Definierar NEAB:s kritiska tillgångar (crown jewels)"""
        return [
            Tillgang(
                id="T001",
                namn="SCADA/DCS",
                beskrivning="Primär styrning och övervakning av elnät och fjärrvärme",
                typ="OT-system",
                kritikalitet="Kritisk",
                ägare="Driftchef",
                beroenden=["T002", "T003", "T008"],
                rto="30 min",
                rpo="5 min",
                klassning="Sekretess"
            ),
            Tillgang(
                id="T002",
                namn="Nätstations-RTU:er",
                beskrivning="Fjärrstyrda enheter i 260 nätstationer",
                typ="OT-utrustning",
                kritikalitet="Kritisk",
                ägare="Driftchef",
                beroenden=["T001"],
                klassning="Skyddsvärd"
            ),
            Tillgang(
                id="T003",
                namn="Driftcentral",
                beskrivning="Kontrollrum med arbetsplatser och historikserver",
                typ="Fysisk anläggning + IT",
                kritikalitet="Kritisk",
                ägare="Driftchef",
                beroenden=["T001", "T008"],
                rto="30 min",
                klassning="Sekretess"
            ),
            Tillgang(
                id="T004",
                namn="AMI/MDM",
                beskrivning="Smarta mätare - insamling, konfiguration, fjärrbryt",
                typ="OT/IT-hybrid",
                kritikalitet="Hög",
                ägare="IT-chef",
                beroenden=["T007", "T008"],
                rto="4 h",
                rpo="15 min",
                klassning="Sekretess"
            ),
            Tillgang(
                id="T005",
                namn="OMS",
                beskrivning="Avbrottshantering och callcenterkoppling",
                typ="IT-system",
                kritikalitet="Hög",
                ägare="Kundservicechef",
                beroenden=["T001", "T007"],
                rto="4 h",
                rpo="15 min",
                klassning="Skyddsvärd"
            ),
            Tillgang(
                id="T006",
                namn="GIS/NIS",
                beskrivning="Nätkarta och tillgångsregister",
                typ="IT-system",
                kritikalitet="Hög",
                ägare="IT-chef",
                klassning="Skyddsvärd"
            ),
            Tillgang(
                id="T007",
                namn="Kund- och faktureringssystem",
                beskrivning="PII, betalflöden, 97000 kunder",
                typ="IT-system",
                kritikalitet="Hög",
                ägare="CFO",
                rto="24 h",
                rpo="4 h",
                klassning="Sekretess"
            ),
            Tillgang(
                id="T008",
                namn="Identitets- och behörighetsplattform",
                beskrivning="AD/AAD, PKI, MFA",
                typ="IT-system",
                kritikalitet="Kritisk",
                ägare="CISO",
                beroenden=[],
                rto="2 h",
                klassning="Sekretess"
            ),
            Tillgang(
                id="T009",
                namn="SIEM och loggplattform",
                beskrivning="Centraliserad loggning och hotdetektering",
                typ="Säkerhetssystem",
                kritikalitet="Hög",
                ägare="CISO",
                rto="12 h",
                klassning="Skyddsvärd"
            ),
            Tillgang(
                id="T010",
                namn="Backup-system",
                beskrivning="Backup och återställning inkl. immutabel backup",
                typ="IT-system",
                kritikalitet="Kritisk",
                ägare="IT-chef",
                klassning="Sekretess"
            ),
            Tillgang(
                id="T011",
                namn="API Gateway (DMZ)",
                beskrivning="Datautbyte mellan IT och OT, externa partners",
                typ="Nätverksinfrastruktur",
                kritikalitet="Hög",
                ägare="IT-chef",
                beroenden=["T001", "T004", "T007"],
                klassning="Skyddsvärd"
            ),
            Tillgang(
                id="T012",
                namn="Mätdata (PII)",
                beskrivning="Historisk elförbrukning per kund, 7-10 år retention",
                typ="Data",
                kritikalitet="Hög",
                ägare="CFO",
                klassning="Sekretess"
            )
        ]

    def _ladda_typisk_hotbild(self) -> List[Dict]:
        """Laddar typiska hot för energisektorn baserat på dokumentation"""
        return [
            {
                "hot": "Ransomware via kontors-IT",
                "stride": HotKategori.DENIAL_OF_SERVICE.value,
                "beskrivning": "Krypterad data och system via phishing, risk för sidoförflyttning mot OT",
                "sannolikhet": Sannolikhet.HOG.value,
                "tillgangar": ["T007", "T008", "T001"],
                "sarbarhet": "Bristande zonindelning IT/OT, delade autentiseringstjänster"
            },
            {
                "hot": "Leverantörskedjeangrepp",
                "stride": HotKategori.TAMPERING.value,
                "beskrivning": "Komprometterat uppdateringsflöde eller fjärrsupportkonto",
                "sannolikhet": Sannolikhet.MEDEL.value,
                "tillgangar": ["T001", "T004"],
                "sarbarhet": "Begränsad kontroll över leverantörsåtkomst, delade konton förekommer"
            },
            {
                "hot": "Phishing / MFA-trötthet",
                "stride": HotKategori.SPOOFING.value,
                "beskrivning": "Stulna autentiseringstokens via social engineering",
                "sannolikhet": Sannolikhet.HOG.value,
                "tillgangar": ["T008", "T007", "T003"],
                "sarbarhet": "Ojämt införande av MFA, användarutbildning behöver förstärkas"
            },
            {
                "hot": "Felkonfigurerad molnresurs",
                "stride": HotKategori.INFORMATION_DISCLOSURE.value,
                "beskrivning": "Exponerad data eller loggflöden via missconfigured cloud storage",
                "sannolikhet": Sannolikhet.MEDEL.value,
                "tillgangar": ["T009", "T012"],
                "sarbarhet": "Komplex molnkonfiguration, manuella säkerhetsinställningar"
            },
            {
                "hot": "Felkonfigurerad API-gateway",
                "stride": HotKategori.INFORMATION_DISCLOSURE.value,
                "beskrivning": "Otillräcklig segmentering exponerar interna system eller driftdata mot internet",
                "sannolikhet": Sannolikhet.MEDEL.value,
                "tillgangar": ["T011", "T001", "T007"],
                "sarbarhet": "Komplex API-arkitektur, otillräcklig dokumentation av segmentering"
            },
            {
                "hot": "Stulna API-nycklar",
                "stride": HotKategori.ELEVATION_OF_PRIVILEGE.value,
                "beskrivning": "Obehörig åtkomst till kunduppgifter via komprometterade API-tokens",
                "sannolikhet": Sannolikhet.MEDEL.value,
                "tillgangar": ["T007", "T011"],
                "sarbarhet": "API-nycklar i klartext i konfigfiler, ingen automatisk rotation"
            },
            {
                "hot": "DDoS-angrepp",
                "stride": HotKategori.DENIAL_OF_SERVICE.value,
                "beskrivning": "Överbelastning av kundportaler och laddtjänster",
                "sannolikhet": Sannolikhet.MEDEL.value,
                "tillgangar": ["T011", "T007"],
                "sarbarhet": "Begränsad DDoS-mitigation för publika tjänster"
            },
            {
                "hot": "OT-manipulation av setpoints",
                "stride": HotKategori.TAMPERING.value,
                "beskrivning": "Otillåten ändring av styrparametrar i SCADA",
                "sannolikhet": Sannolikhet.LAG.value,
                "tillgangar": ["T001", "T002"],
                "sarbarhet": "Delade konton i äldre OT-system, begränsad loggning av kommandohistorik"
            },
            {
                "hot": "Replay-attack på OT-protokoll",
                "stride": HotKategori.TAMPERING.value,
                "beskrivning": "Återanvändning av legitima kommandon (IEC 60870-5-104)",
                "sannolikhet": Sannolikhet.LAG.value,
                "tillgangar": ["T001", "T002"],
                "sarbarhet": "Äldre protokoll utan kryptografi eller sekvensverifiering"
            },
            {
                "hot": "Missbruk av fjärrbryt i AMI",
                "stride": HotKategori.DENIAL_OF_SERVICE.value,
                "beskrivning": "Massdiskonnektion av kunder via komprometterat MDM-system",
                "sannolikhet": Sannolikhet.LAG.value,
                "tillgangar": ["T004"],
                "sarbarhet": "Beroende av enskild AMI-leverantör, bristande segmentering"
            },
            {
                "hot": "Insiderhot",
                "stride": HotKategori.ELEVATION_OF_PRIVILEGE.value,
                "beskrivning": "Obehörig åtkomst eller avvikelse från rutiner av välmenande men stressad personal",
                "sannolikhet": Sannolikhet.MEDEL.value,
                "tillgangar": ["T001", "T003", "T007"],
                "sarbarhet": "Otydlig behörighetsstyrning, stress under högsäsong"
            }
        ]

    def genomför_workshop(self, input_data: Optional[Dict],
                          regulatorisk_data: Dict) -> Dict[str, Any]:
        """
        Genomför komplett riskworkshop enligt MSB:s metod

        Args:
            input_data: Input från formulär
            regulatorisk_data: Resultat från regulatorisk kartläggning

        Returns:
            Riskregister med alla identifierade risker
        """
        logger.info("Startar riskworkshop...")

        # Steg 1: Identifiera hot och sårbarheter
        risker = self._identifiera_risker(input_data, regulatorisk_data)

        # Steg 2: Bedöm konsekvens och sannolikhet
        risker = self._bedom_risker(risker)

        # Steg 3: Rangordna risker
        risker = sorted(risker, key=lambda r: r.riskvarde, reverse=True)

        # Steg 4: Koppla till regelverk
        risker = self._koppla_till_regelverk(risker, regulatorisk_data)

        resultat = {
            "risker": [self._risk_till_dict(r) for r in risker],
            "riskmatris": self._skapa_riskmatris(risker),
            "sammanfattning": self._generera_risksammanfattning(risker),
            "top_risker": [self._risk_till_dict(r) for r in risker[:10]],
            "tillgangar": [self._tillgang_till_dict(t) for t in self.tillgangar]
        }

        logger.info(f"Workshop klar: {len(risker)} risker identifierade")
        return resultat

    def _identifiera_risker(self, input_data: Optional[Dict],
                            regulatorisk_data: Dict) -> List[Risk]:
        """Identifierar risker baserat på hot och sårbarheter"""
        risker = []
        risk_id_counter = 1

        # Använd typisk hotbild som bas
        for hot_scenario in self.typiska_hot:
            for tillgang_id in hot_scenario["tillgangar"]:
                tillgang = next((t for t in self.tillgangar if t.id == tillgang_id), None)
                if not tillgang:
                    continue

                # Bedöm konsekvens baserat på tillgångens kritikalitet och CIA
                konsekvens_cia = self._bestam_cia_paverkan(hot_scenario["stride"])
                konsekvens_niva = self._bestam_konsekvens(tillgang, konsekvens_cia)

                risk = Risk(
                    id=f"R{risk_id_counter:03d}",
                    tillgang_id=tillgang.id,
                    tillgang_namn=tillgang.namn,
                    hot_beskrivning=hot_scenario["hot"],
                    hot_kategori=hot_scenario["stride"],
                    sarbarhet=hot_scenario["sarbarhet"],
                    konsekvens_beskrivning=self._beskriv_konsekvens(tillgang, konsekvens_cia),
                    konsekvens_cia=konsekvens_cia,
                    konsekvens_niva=konsekvens_niva,
                    sannolikhet_niva=hot_scenario["sannolikhet"],
                    riskvarde=konsekvens_niva * hot_scenario["sannolikhet"],
                    riskniva=self._bestam_riskniva(konsekvens_niva * hot_scenario["sannolikhet"]),
                    befintliga_kontroller=self._identifiera_befintliga_kontroller(tillgang),
                    kommentar=hot_scenario["beskrivning"]
                )

                risker.append(risk)
                risk_id_counter += 1

        # Lägg till regulatoriska risker (brister i efterlevnad)
        for krav in regulatorisk_data.get("krav", []):
            if krav["Status"] in ["Ej uppfyllt", "Delvis uppfyllt"]:
                risk = Risk(
                    id=f"R{risk_id_counter:03d}",
                    tillgang_id="TREG",
                    tillgang_namn="Regelefterlevnad",
                    hot_beskrivning=f"Bristande efterlevnad av {krav['Regelverk']} {krav['Artikel']}",
                    hot_kategori="Regulatorisk risk",
                    sarbarhet=krav.get("Gap-analys", ""),
                    konsekvens_beskrivning="Sanktionsavgifter, rättsliga konsekvenser, reputationsskada",
                    konsekvens_cia=["C", "I", "A"],
                    konsekvens_niva=4 if krav["Status"] == "Ej uppfyllt" else 3,
                    sannolikhet_niva=3,
                    riskvarde=(4 if krav["Status"] == "Ej uppfyllt" else 3) * 3,
                    riskniva=self._bestam_riskniva((4 if krav["Status"] == "Ej uppfyllt" else 3) * 3),
                    koppling_regelverk=[f"{krav['Regelverk']} {krav['Artikel']}"]
                )
                risker.append(risk)
                risk_id_counter += 1

        return risker

    def _bedom_risker(self, risker: List[Risk]) -> List[Risk]:
        """Gör detaljerad bedömning av varje risk"""
        # I en riktig workshop skulle detta göras interaktivt
        # För nu: använd förkonfigurerade värden
        return risker

    def _bestam_cia_paverkan(self, stride_kategori: str) -> List[str]:
        """Mappar STRIDE till CIA-påverkan"""
        mapping = {
            HotKategori.SPOOFING.value: ["C", "I"],
            HotKategori.TAMPERING.value: ["I"],
            HotKategori.REPUDIATION.value: ["I"],
            HotKategori.INFORMATION_DISCLOSURE.value: ["C"],
            HotKategori.DENIAL_OF_SERVICE.value: ["A"],
            HotKategori.ELEVATION_OF_PRIVILEGE.value: ["C", "I", "A"],
            "Regulatorisk risk": ["C", "I", "A"]
        }
        return mapping.get(stride_kategori, ["C", "I", "A"])

    def _bestam_konsekvens(self, tillgang: Tillgang, cia_paverkan: List[str]) -> int:
        """Bedömer konsekvensnivå (1-5) baserat på tillgång och CIA-påverkan"""
        kritikalitet_mapping = {
            "Kritisk": 5,
            "Hög": 4,
            "Medel": 3,
            "Låg": 2
        }

        bas_konsekvens = kritikalitet_mapping.get(tillgang.kritikalitet, 3)

        # Justera baserat på CIA-påverkan
        if "A" in cia_paverkan and tillgang.rto and "min" in tillgang.rto:
            # Tillgänglighet kritisk med snabb RTO
            bas_konsekvens = min(5, bas_konsekvens + 1)

        return bas_konsekvens

    def _beskriv_konsekvens(self, tillgang: Tillgang, cia_paverkan: List[str]) -> str:
        """Genererar konsekvensbeskrivning"""
        beskrivningar = []

        if "C" in cia_paverkan:
            if tillgang.klassning == "Sekretess":
                beskrivningar.append("Läckage av känslig information")

        if "I" in cia_paverkan:
            if tillgang.typ in ["OT-system", "OT-utrustning"]:
                beskrivningar.append("Risk för felaktig styrning med personsäkerhetskonsekvenser")
            else:
                beskrivningar.append("Korrupta data påverkar beslutsunderlag")

        if "A" in cia_paverkan:
            if tillgang.kritikalitet == "Kritisk":
                beskrivningar.append(f"Driftstopp, målvärde: RTO {tillgang.rto or 'ej definierat'}")

        return "; ".join(beskrivningar) if beskrivningar else "Påverkan på verksamheten"

    def _bestam_riskniva(self, riskvarde: int) -> str:
        """Bestämmer risknivå baserat på riskvärde"""
        if riskvarde >= 15:
            return "Mycket hög"
        elif riskvarde >= 10:
            return "Hög"
        elif riskvarde >= 5:
            return "Medel"
        else:
            return "Låg"

    def _identifiera_befintliga_kontroller(self, tillgang: Tillgang) -> List[str]:
        """Identifierar befintliga säkerhetskontroller för tillgång"""
        kontroller = []

        if tillgang.typ in ["OT-system", "OT-utrustning"]:
            kontroller.extend([
                "Segmenterat OT-nät (VLAN)",
                "Bastion-värdar för fjärråtkomst",
                "24/7 driftbevakning"
            ])

        if tillgang.klassning == "Sekretess":
            kontroller.extend([
                "Åtkomstkontroll (delvis MFA)",
                "Loggning till SIEM"
            ])

        if tillgang.rto:
            kontroller.append(f"Backup med RTO {tillgang.rto}")

        return kontroller

    def _koppla_till_regelverk(self, risker: List[Risk],
                               regulatorisk_data: Dict) -> List[Risk]:
        """Kopplar risker till relevanta regelverk"""
        for risk in risker:
            # Mappa hot till regelverk
            if "Ransomware" in risk.hot_beskrivning or "DDoS" in risk.hot_beskrivning:
                risk.koppling_regelverk.append("NIS2 Art. 21")

            if "PII" in risk.tillgang_namn or risk.tillgang_id == "T007":
                risk.koppling_regelverk.append("GDPR Art. 32")

            if "SCADA" in risk.tillgang_namn or risk.tillgang_id == "T001":
                risk.koppling_regelverk.extend(["NIS2 Art. 21", "CER Kap. II"])

        return risker

    def _skapa_riskmatris(self, risker: List[Risk]) -> Dict:
        """Skapar riskmatris för visualisering"""
        matris = {}
        for s in range(1, 5):  # Sannolikhet 1-4
            for k in range(1, 6):  # Konsekvens 1-5
                matris[f"S{s}_K{k}"] = []

        for risk in risker:
            key = f"S{risk.sannolikhet_niva}_K{risk.konsekvens_niva}"
            if key in matris:
                matris[key].append(risk.id)

        return matris

    def _generera_risksammanfattning(self, risker: List[Risk]) -> str:
        """Genererar textsammanfattning av riskbilden"""
        mycket_hog = sum(1 for r in risker if r.riskniva == "Mycket hög")
        hog = sum(1 for r in risker if r.riskniva == "Hög")
        medel = sum(1 for r in risker if r.riskniva == "Medel")
        lag = sum(1 for r in risker if r.riskniva == "Låg")

        return f"""
Riskworkshop identifierade {len(risker)} risker:
- {mycket_hog} mycket höga risker (kräver omedelbar åtgärd)
- {hog} höga risker (prioriterad hantering)
- {medel} medelhöga risker (planerad hantering)
- {lag} låga risker (övervakning)

Top 3 risker:
1. {risker[0].hot_beskrivning} ({risker[0].tillgang_namn})
2. {risker[1].hot_beskrivning} ({risker[1].tillgang_namn})
3. {risker[2].hot_beskrivning} ({risker[2].tillgang_namn})
        """.strip()

    def generera_åtgärdsplan(self, risk_data: Dict,
                             regulatorisk_data: Dict) -> Dict[str, Any]:
        """
        Genererar riskbehandlingsplan med åtgärder

        Args:
            risk_data: Resultat från riskworkshop
            regulatorisk_data: Regulatoriska brister

        Returns:
            Åtgärdsplan med CIS Controls-mappning
        """
        logger.info("Genererar åtgärdsplan...")

        åtgärder = []
        åtgärd_id_counter = 1

        # Generera åtgärder för top-risker
        for risk_dict in risk_data["top_risker"]:
            if risk_dict["Risknivå"] in ["Mycket hög", "Hög"]:
                åtgärd = self._generera_åtgärd_för_risk(risk_dict, åtgärd_id_counter)
                if åtgärd:
                    åtgärder.append(åtgärd)
                    åtgärd_id_counter += 1

        # Generera åtgärder för regulatoriska brister
        for prioriterad in regulatorisk_data.get("prioriterade_åtgärder", [])[:5]:
            åtgärd = Atgard(
                id=f"Å{åtgärd_id_counter:03d}",
                risk_id="RREG",
                beskrivning=prioriterad["åtgärd"],
                strategi="Reducera",
                cis_controls=self._identifiera_cis_for_regelverk(prioriterad["artikel"]),
                ansvarig_roll="CISO",
                planerat_datum=(datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                kostnad="M",
                effekt="H",
                kvarvarande_risk="Låg"
            )
            åtgärder.append(åtgärd)
            åtgärd_id_counter += 1

        resultat = {
            "åtgärder": [self._åtgärd_till_dict(a) for a in åtgärder],
            "sammanfattning": f"Identifierade {len(åtgärder)} prioriterade åtgärder",
            "budget_estimat": self._beräkna_budget(åtgärder),
            "tidslinje": self._skapa_tidslinje(åtgärder)
        }

        logger.info(f"Åtgärdsplan klar: {len(åtgärder)} åtgärder")
        return resultat

    def _generera_åtgärd_för_risk(self, risk: Dict, id_num: int) -> Optional[Atgard]:
        """Genererar åtgärd för en specifik risk"""

        # Mappning: hot -> åtgärd
        åtgärds_mallar = {
            "Ransomware": Atgard(
                id=f"Å{id_num:03d}",
                risk_id=risk["Risk-ID"],
                beskrivning="Implementera Zero Trust-segmentering mellan IT och OT. Inför EDR på alla endpoints.",
                strategi="Reducera",
                cis_controls=["CIS 4.1", "CIS 4.2", "CIS 10.1", "CIS 13.2"],
                ansvarig_roll="IT-chef / OT-säkerhetsansvarig",
                planerat_datum=(datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d"),
                kostnad="H",
                effekt="H",
                kvarvarande_risk="Medel",
                implementation_steg=[
                    "Kartlägg alla dataflöden IT-OT",
                    "Upphandla EDR-lösning",
                    "Implementera mikrosegmentering",
                    "Testa återställning från backup"
                ]
            ),
            "Leverantörskedjeangrepp": Atgard(
                id=f"Å{id_num:03d}",
                risk_id=risk["Risk-ID"],
                beskrivning="Inför PAM (Privileged Access Management) för all leverantörsåtkomst med MFA och tidsbegränsning",
                strategi="Reducera",
                cis_controls=["CIS 5.3", "CIS 5.4", "CIS 6.3"],
                ansvarig_roll="CISO",
                planerat_datum=(datetime.now() + timedelta(days=120)).strftime("%Y-%m-%d"),
                kostnad="M",
                effekt="H",
                kvarvarande_risk="Låg",
                implementation_steg=[
                    "Upphandla PAM-lösning",
                    "Inventera alla leverantörsåtkomster",
                    "Konfigurera MFA för fjärråtkomst",
                    "Utbilda leverantörer"
                ]
            ),
            "Phishing": Atgard(
                id=f"Å{id_num:03d}",
                risk_id=risk["Risk-ID"],
                beskrivning="Komplettera MFA-införande till 100%. Genomför obligatorisk phishing-utbildning kvartalsvis.",
                strategi="Reducera",
                cis_controls=["CIS 6.3", "CIS 6.5", "CIS 14.2"],
                ansvarig_roll="CISO / HR",
                planerat_datum=(datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
                kostnad="L",
                effekt="M",
                kvarvarande_risk="Medel",
                implementation_steg=[
                    "Kartlägg system utan MFA",
                    "Utöka MFA-krav",
                    "Upphandla phishing-simuleringsplattform",
                    "Genomför första kampanj"
                ]
            ),
            "API": Atgard(
                id=f"Å{id_num:03d}",
                risk_id=risk["Risk-ID"],
                beskrivning="Implementera API-säkerhetslösning med rate limiting, token rotation och logging",
                strategi="Reducera",
                cis_controls=["CIS 3.3", "CIS 6.2", "CIS 8.2"],
                ansvarig_roll="IT-chef",
                planerat_datum=(datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                kostnad="M",
                effekt="H",
                kvarvarande_risk="Låg",
                implementation_steg=[
                    "Inventera alla API:er",
                    "Implementera API Gateway med säkerhetspolicy",
                    "Konfigurera automatisk nyckelrotation",
                    "Aktivera API-loggning till SIEM"
                ]
            )
        }

        # Identifiera relevant mall baserat på hotbeskrivning
        for nyckelord, mall in åtgärds_mallar.items():
            if nyckelord.lower() in risk["Hot"].lower():
                mall.id = f"Å{id_num:03d}"
                mall.risk_id = risk["Risk-ID"]
                return mall

        # Default åtgärd om ingen specifik mall matchar
        return Atgard(
            id=f"Å{id_num:03d}",
            risk_id=risk["Risk-ID"],
            beskrivning=f"Åtgärda identifierad risk: {risk['Hot']}",
            strategi="Reducera",
            cis_controls=["CIS 4.1"],
            ansvarig_roll="CISO",
            planerat_datum=(datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
            kostnad="M",
            effekt="M",
            kvarvarande_risk="Medel"
        )

    def _identifiera_cis_for_regelverk(self, artikel: str) -> List[str]:
        """Mappar regelverksartikel till CIS Controls"""
        mapping = {
            "Art. 21": ["CIS 1", "CIS 4", "CIS 5"],
            "Art. 23": ["CIS 17"],
            "Art. 32": ["CIS 3", "CIS 8", "CIS 10"]
        }
        return mapping.get(artikel, ["CIS 4"])

    def _beräkna_budget(self, åtgärder: List[Atgard]) -> str:
        """Beräknar total budgetuppskattning"""
        kostnad_mapping = {"L": 50000, "M": 200000, "H": 800000}
        total = sum(kostnad_mapping.get(a.kostnad, 200000) for a in åtgärder)
        return f"{total:,.0f} SEK".replace(",", " ")

    def _skapa_tidslinje(self, åtgärder: List[Atgard]) -> Dict:
        """Skapar tidslinje för åtgärder"""
        sorterade = sorted(åtgärder, key=lambda a: a.planerat_datum)
        return {
            "första_åtgärd": sorterade[0].planerat_datum if sorterade else "N/A",
            "sista_åtgärd": sorterade[-1].planerat_datum if sorterade else "N/A",
            "total_tidsram": "6-12 månader"
        }

    def _risk_till_dict(self, risk: Risk) -> Dict:
        """Konverterar Risk till dictionary för Excel/rapport"""
        return {
            "Risk-ID": risk.id,
            "Tillgång / område": risk.tillgang_namn,
            "Hot": risk.hot_beskrivning,
            "STRIDE": risk.hot_kategori,
            "Sårbarhet": risk.sarbarhet,
            "Konsekvens": risk.konsekvens_beskrivning,
            "CIA-påverkan": ", ".join(risk.konsekvens_cia),
            "Konsekvensnivå": risk.konsekvens_niva,
            "Sannolikhet": risk.sannolikhet_niva,
            "Riskvärde": risk.riskvarde,
            "Risknivå": risk.riskniva,
            "Befintliga kontroller": "; ".join(risk.befintliga_kontroller),
            "Regelverk": "; ".join(risk.koppling_regelverk),
            "Kommentar": risk.kommentar
        }

    def _åtgärd_till_dict(self, åtgärd: Atgard) -> Dict:
        """Konverterar Åtgärd till dictionary"""
        return {
            "Åtgärds-ID": åtgärd.id,
            "Risk-ID": åtgärd.risk_id,
            "Beskrivning": åtgärd.beskrivning,
            "Strategi": åtgärd.strategi,
            "CIS Controls": ", ".join(åtgärd.cis_controls),
            "Ansvarig roll": åtgärd.ansvarig_roll,
            "Planerat datum": åtgärd.planerat_datum,
            "Kostnad": åtgärd.kostnad,
            "Effekt": åtgärd.effekt,
            "Status": åtgärd.status,
            "Kvarvarande risk": åtgärd.kvarvarande_risk,
            "Implementation": "; ".join(åtgärd.implementation_steg)
        }

    def _tillgang_till_dict(self, tillgang: Tillgang) -> Dict:
        """Konverterar Tillgång till dictionary"""
        return {
            "ID": tillgang.id,
            "Namn": tillgang.namn,
            "Beskrivning": tillgang.beskrivning,
            "Typ": tillgang.typ,
            "Kritikalitet": tillgang.kritikalitet,
            "Ägare": tillgang.ägare,
            "RTO": tillgang.rto or "N/A",
            "RPO": tillgang.rpo or "N/A",
            "Klassning": tillgang.klassning,
            "Beroenden": ", ".join(tillgang.beroenden)
        }