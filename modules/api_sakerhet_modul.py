"""
API-Säkerhetsmodul
==================
Analyserar API-säkerhet för B2B och B2C-scenarios med fokus på
kryptering, autentisering, risker och regulatorisk påverkan

Del av: NEAB Security Assessment Suite
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class APITyp(Enum):
    """Typ av API"""
    B2B = "Business-to-Business"
    B2C = "Business-to-Consumer"


class Autentiseringsmetod(Enum):
    """Autentiseringsmetoder för API:er"""
    API_KEY = "API-nyckel"
    OAUTH2 = "OAuth 2.0"
    JWT = "JSON Web Token"
    MTLS = "Mutual TLS"
    SAML = "SAML"
    BASIC_AUTH = "Basic Authentication"


class Krypteringsniva(Enum):
    """Krypteringsnivåer"""
    INGEN = "Ingen kryptering"
    TRANSPORT = "Kryptering i transport (TLS)"
    END_TO_END = "End-to-end-kryptering"
    TRANSPORT_OCH_DATA = "Transport + data-at-rest kryptering"


@dataclass
class APIScenario:
    """Representerar ett API-scenario"""
    scenario_id: str
    typ: str  # B2B eller B2C
    namn: str
    beskrivning: str
    dataflöde: str
    kryptering: str
    kryptering_detaljer: Dict[str, str]
    autentisering: List[str]
    autentisering_detaljer: Dict[str, str]
    risker: List[Dict[str, str]]
    mitigeringar: List[Dict[str, str]]
    regelverk: List[str]
    cis_controls: List[str]
    kommentar: str = ""


class APISakerhetAnalys:
    """
    Hanterar analys av API-säkerhet för B2B och B2C
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.organisation = config.get("organisation", {})

        # Förkonfigurerade scenarios för NEAB
        self.b2b_scenarios = self._definiera_b2b_scenarios()
        self.b2c_scenarios = self._definiera_b2c_scenarios()

        logger.info("API-säkerhetsmodul initierad")

    def _definiera_b2b_scenarios(self) -> List[APIScenario]:
        """Definierar typiska B2B-scenarios för NEAB"""
        return [
            APIScenario(
                scenario_id="B2B-01",
                typ=APITyp.B2B.value,
                namn="Mätdataöverföring till PayGrid (faktura)",
                beskrivning="Daglig överföring av aggregerad mätdata till faktureringspartner",
                dataflöde="""
1. NEAB MDM-system aggregerar mätdata (natt)
2. API-Gateway (DMZ) exponerar REST-endpoint
3. PayGrid hämtar data via GET /api/v1/meteringdata
4. Mätdata (JSON) innehåller: kund-ID, period, förbrukning kWh
5. PayGrid använder data för fakturagenererering
                """.strip(),
                kryptering=Krypteringsniva.TRANSPORT_OCH_DATA.value,
                kryptering_detaljer={
                    "Transport": "TLS 1.3 med certifikatpinning",
                    "Data-at-rest": "AES-256 för lagrade mätdata",
                    "Algoritm": "TLS_AES_256_GCM_SHA384",
                    "Certifikat": "EV SSL från DigiCert"
                },
                autentisering=[Autentiseringsmetod.MTLS.value, Autentiseringsmetod.API_KEY.value],
                autentisering_detaljer={
                    "Primär": "Mutual TLS (client certificate)",
                    "Sekundär": "Roterad API-nyckel (30 dagars livstid)",
                    "IP-whitelisting": "PayGrid statiska IP-adresser",
                    "Rate limiting": "1000 requests/timme"
                },
                risker=[
                    {
                        "risk": "Komprometterad API-nyckel",
                        "beskrivning": "Om PayGrids API-nyckel läcker kan obehöriga hämta mätdata",
                        "påverkan": "Konfidentialitetsbrott (GDPR Art. 32)",
                        "sannolikhet": "Medel"
                    },
                    {
                        "risk": "Man-in-the-middle under nyckelutbyte",
                        "beskrivning": "Avlyssning vid initial nyckelöverföring",
                        "påverkan": "Exponering av autentiseringsdata",
                        "sannolikhet": "Låg"
                    },
                    {
                        "risk": "Leverantörsincident (PayGrid)",
                        "beskrivning": "Säkerhetsbrott hos PayGrid påverkar NEAB-data",
                        "påverkan": "Personuppgiftsincident, rapporteringsskyldighet",
                        "sannolikhet": "Låg"
                    }
                ],
                mitigeringar=[
                    {
                        "åtgärd": "Implementera automatisk nyckelrotation (30 dagar)",
                        "cis": "CIS 3.11",
                        "prioritet": "Hög"
                    },
                    {
                        "åtgärd": "Kryptera API-nycklar med HSM vid överföring",
                        "cis": "CIS 3.3",
                        "prioritet": "Hög"
                    },
                    {
                        "åtgärd": "Regelbunden säkerhetsrevision av PayGrid (årlig)",
                        "cis": "CIS 15.1",
                        "prioritet": "Medel"
                    },
                    {
                        "åtgärd": "Aktivera detaljerad API-loggning till SIEM",
                        "cis": "CIS 8.2",
                        "prioritet": "Hög"
                    }
                ],
                regelverk=["GDPR Art. 32", "NIS2 Art. 21"],
                cis_controls=["CIS 3.3", "CIS 3.11", "CIS 8.2", "CIS 13.2", "CIS 15.1"]
            ),
            APIScenario(
                scenario_id="B2B-02",
                typ=APITyp.B2B.value,
                namn="SCADA fjärrsupport (leverantör)",
                beskrivning="Leverantörens fjärråtkomst till SCADA-system via API-gateway",
                dataflöde="""
1. SCADA-leverantör initierar session via VPN
2. Leverantör autentiserar mot PAM-system
3. Tidsbegränsad session (4h) etableras
4. API-Gateway tillåter åtkomst till SCADA-miljö
5. All aktivitet loggas och spelas in
                """.strip(),
                kryptering=Krypteringsniva.TRANSPORT_OCH_DATA.value,
                kryptering_detaljer={
                    "VPN": "IPsec med AES-256",
                    "Session": "Krypterad VNC över SSH tunnel",
                    "Logging": "Krypterad videoinspelung av session"
                },
                autentisering=[
                    Autentiseringsmetod.MTLS.value,
                    "MFA (TOTP)",
                    "Just-in-time access"
                ],
                autentisering_detaljer={
                    "Primär": "Mutual TLS + MFA",
                    "JIT": "Tidstyrd privilegiehöjning (4h)",
                    "Approval": "Godkännande av driftchef krävs",
                    "Monitoring": "Real-time övervakning av SOC"
                },
                risker=[
                    {
                        "risk": "Leverantörskontots kompromett",
                        "beskrivning": "Attackerare får tillgång via stulna leverantörs-credentials",
                        "påverkan": "Fullständig kontroll över SCADA, sabotage-risk",
                        "sannolikhet": "Medel"
                    },
                    {
                        "risk": "Insiderhot från leverantör",
                        "beskrivning": "Illvillig leverantörsanställd missbrukar åtkomst",
                        "påverkan": "Datatheft, sabotage",
                        "sannolikhet": "Låg"
                    },
                    {
                        "risk": "Persistent access (backdoor)",
                        "beskrivning": "Leverantör installerar obehörig backdoor",
                        "påverkan": "Långvarig obehörig åtkomst",
                        "sannolikhet": "Låg"
                    }
                ],
                mitigeringar=[
                    {
                        "åtgärd": "Implementera PAM med sessionsinspelning",
                        "cis": "CIS 5.4",
                        "prioritet": "Kritisk"
                    },
                    {
                        "åtgärd": "Network segmentation med granulär ACL",
                        "cis": "CIS 12.2",
                        "prioritet": "Hög"
                    },
                    {
                        "åtgärd": "Real-time anomalidetektering på leverantörsaccess",
                        "cis": "CIS 13.7",
                        "prioritet": "Hög"
                    },
                    {
                        "åtgärd": "Post-session integrity check",
                        "cis": "CIS 3.14",
                        "prioritet": "Medel"
                    }
                ],
                regelverk=["NIS2 Art. 21", "CER Kap. II"],
                cis_controls=["CIS 5.4", "CIS 6.3", "CIS 12.2", "CIS 13.7"],
                kommentar="Extremt känslig åtkomst - kräver högsta säkerhetsnivå"
            )
        ]

    def _definiera_b2c_scenarios(self) -> List[APIScenario]:
        """Definierar typiska B2C-scenarios för NEAB"""
        return [
            APIScenario(
                scenario_id="B2C-01",
                typ=APITyp.B2C.value,
                namn="Mobilapp: Elförbrukning och fakturor",
                beskrivning="Kunders åtkomst till sin elförbrukning via NEAB:s mobilapp",
                dataflöde="""
1. Kund öppnar NEAB-appen (iOS/Android)
2. Inloggning via BankID eller användarnamn/lösenord + MFA
3. App anropar REST API: GET /api/customer/consumption
4. Backend validerar JWT-token
5. API hämtar data från kundsystem och returnerar JSON
6. App visualiserar förbrukning och fakturor
                """.strip(),
                kryptering=Krypteringsniva.TRANSPORT.value,
                kryptering_detaljer={
                    "Transport": "TLS 1.3",
                    "Certifikat": "Let's Encrypt",
                    "Certificate pinning": "Aktiverad i app",
                    "Data-at-rest": "Ej krypterad i app (cache töms vid utlogg)"
                },
                autentisering=[
                    Autentiseringsmetod.JWT.value,
                    "BankID",
                    "MFA (SMS/TOTP)"
                ],
                autentisering_detaljer={
                    "Inloggning": "BankID (primär) eller användarnamn + MFA",
                    "Session": "JWT med 15 min livstid, refresh token 7 dagar",
                    "Token": "Signerad med RS256",
                    "Biometri": "Touch ID/Face ID för app-återkomst"
                },
                risker=[
                    {
                        "risk": "Stulna JWT-tokens",
                        "beskrivning": "Attackerare får tag på giltig JWT och kan personifiera kund",
                        "påverkan": "Åtkomst till personuppgifter och förbrukningsdata",
                        "sannolikhet": "Medel"
                    },
                    {
                        "risk": "API-endpoint-brute force",
                        "beskrivning": "Attackerare försöker gissa kund-ID för att få andras data",
                        "påverkan": "Massiv personuppgiftsincident (GDPR)",
                        "sannolikhet": "Medel"
                    },
                    {
                        "risk": "Man-in-the-middle på osäkert WiFi",
                        "beskrivning": "Avlyssning av API-trafik på publikt nätverk",
                        "påverkan": "Läckage av förbrukningsdata och personuppgifter",
                        "sannolikhet": "Låg (tack vare certificate pinning)"
                    },
                    {
                        "risk": "Session hijacking",
                        "beskrivning": "Komprometterad enhet -> stulna refresh tokens",
                        "påverkan": "Långvarig obehörig åtkomst",
                        "sannolikhet": "Låg"
                    }
                ],
                mitigeringar=[
                    {
                        "åtgärd": "Implementera strikt rate limiting (100 req/min per kund)",
                        "cis": "CIS 13.2",
                        "prioritet": "Hög"
                    },
                    {
                        "åtgärd": "Backend validering: auktorisera kund-ID mot JWT claims",
                        "cis": "CIS 6.8",
                        "prioritet": "Kritisk"
                    },
                    {
                        "åtgärd": "Token binding till enhets-fingerprint",
                        "cis": "CIS 6.3",
                        "prioritet": "Hög"
                    },
                    {
                        "åtgärd": "Anomalidetektering: flagga omöjliga resor (geo-location)",
                        "cis": "CIS 13.7",
                        "prioritet": "Medel"
                    },
                    {
                        "åtgärd": "Implementera token revocation-lista",
                        "cis": "CIS 6.2",
                        "prioritet": "Medel"
                    }
                ],
                regelverk=["GDPR Art. 5", "GDPR Art. 32"],
                cis_controls=["CIS 6.2", "CIS 6.3", "CIS 6.8", "CIS 13.2", "CIS 13.7"],
                kommentar="97 000 potentiella användare - hög exponering"
            ),
            APIScenario(
                scenario_id="B2C-02",
                typ=APITyp.B2C.value,
                namn="Webbportal: Rapportera felavbrott",
                beskrivning="Kunder rapporterar elavbrott via NEAB:s webbplats",
                dataflöde="""
1. Kund besöker neab.se/felavbrott
2. Formulär: adress, beskrivning, kontaktuppgifter
3. POST /api/incidents/report (ingen autentisering krävs)
4. API sparar rapport i OMS-system
5. Automatisk bekräftelse via SMS skickas
6. Driftcentral får notifiering
                """.strip(),
                kryptering=Krypteringsniva.TRANSPORT.value,
                kryptering_detaljer={
                    "Transport": "TLS 1.2+ (obligatorisk)",
                    "Formulärdata": "HTTPS POST",
                    "SMS": "Skickas via säker operatörs-API"
                },
                autentisering=["Ingen autentisering (öppet API)", "reCAPTCHA v3"],
                autentisering_detaljer={
                    "Autentisering": "Ingen (öppen endpoint för allmänheten)",
                    "Bot-skydd": "reCAPTCHA v3 med score-baserad filtrering",
                    "Rate limiting": "5 rapporter/IP-adress/timme"
                },
                risker=[
                    {
                        "risk": "Spam och falska rapporter",
                        "beskrivning": "Bottar eller trolls överöser systemet med falska felanmälningar",
                        "påverkan": "Överlastning av OMS, driftcentralen hanterar falska larm",
                        "sannolikhet": "Hög"
                    },
                    {
                        "risk": "DDoS-attack på endpoint",
                        "beskrivning": "Massiv överbelastning av felanmälan-API",
                        "påverkan": "Legitima kunder kan inte rapportera avbrott",
                        "sannolikhet": "Medel"
                    },
                    {
                        "risk": "Injection-attacker (SQL/XSS)",
                        "beskrivning": "Illvillig payload i fritextfält",
                        "påverkan": "Databaskompromiss eller XSS i driftcentral-UI",
                        "sannolikhet": "Medel"
                    }
                ],
                mitigeringar=[
                    {
                        "åtgärd": "Robust input validation och sanitization",
                        "cis": "CIS 16.1",
                        "prioritet": "Kritisk"
                    },
                    {
                        "åtgärd": "DDoS-skydd via CDN (Cloudflare/Akamai)",
                        "cis": "CIS 13.2",
                        "prioritet": "Hög"
                    },
                    {
                        "åtgärd": "reCAPTCHA v3 med adaptive rate limiting",
                        "cis": "CIS 13.2",
                        "prioritet": "Hög"
                    },
                    {
                        "åtgärd": "Content Security Policy (CSP) headers",
                        "cis": "CIS 16.4",
                        "prioritet": "Medel"
                    },
                    {
                        "åtgärd": "Honeypot-fält i formulär för bot-detektion",
                        "cis": "CIS 13.3",
                        "prioritet": "Låg"
                    }
                ],
                regelverk=["NIS2 Art. 21 (tillgänglighet)"],
                cis_controls=["CIS 13.2", "CIS 16.1", "CIS 16.4"],
                kommentar="Kritisk under stormar/kriser - måste vara tillgänglig"
            )
        ]

    def analysera_scenarios(self, input_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Genomför komplett API-säkerhetsanalys

        Args:
            input_data: Data från formulär (valfritt)

        Returns:
            Analysresultat för alla scenarios
        """
        logger.info("Startar API-säkerhetsanalys...")

        # Samla alla scenarios
        alla_scenarios = self.b2b_scenarios + self.b2c_scenarios

        # Analysera varje scenario
        analyserade = [self._analysera_scenario(s) for s in alla_scenarios]

        # Jämförande analys
        jamforelse = self._jamfor_b2b_b2c()

        resultat = {
            "scenarios": [self._scenario_till_dict(s) for s in alla_scenarios],
            "jamforelse_b2b_b2c": jamforelse,
            "sammanfattning": self._generera_api_sammanfattning(alla_scenarios),
            "kritiska_risker": self._identifiera_kritiska_api_risker(alla_scenarios),
            "regulatorisk_koppling": self._koppla_api_till_regelverk(alla_scenarios)
        }

        logger.info(f"API-analys klar: {len(alla_scenarios)} scenarios analyserade")
        return resultat

    def _analysera_scenario(self, scenario: APIScenario) -> APIScenario:
        """Gör djupanalys av enskilt scenario"""
        # I produktion: mer detaljerad analys
        return scenario

    def _jamfor_b2b_b2c(self) -> Dict[str, Any]:
        """Jämför B2B och B2C ur säkerhetsperspektiv"""
        return {
            "autentisering": {
                "B2B": "Starkare krav: Mutual TLS, API-nycklar med rotation, ofta kombinerat med IP-whitelisting",
                "B2C": "Användarvänlighet prioriteras: BankID, JWT med kortare livstid, biometrisk återaukt.",
                "skillnad": "B2B fokuserar på maskin-till-maskin-trust med långlivade credentials. B2C balanserar säkerhet mot UX."
            },
            "kryptering": {
                "B2B": "End-to-end + data-at-rest. Ofta krav på HSM för nyckelhantering.",
                "B2C": "Primärt TLS i transport. Certificate pinning i mobilappar. Data-at-rest mindre vanligt.",
                "skillnad": "B2B hanterar ofta större volymer känslig data som kräver starkare kryptering."
            },
            "rate_limiting": {
                "B2B": "Högre gränser (1000+ req/h) för batchöverföringar",
                "B2C": "Lägre gränser (100 req/min) per användare",
                "skillnad": "B2B-partners är kända och trusted. B2C måste skydda mot DDoS från okända källor."
            },
            "regulatorisk_paverkan": {
                "B2B": "NIS2 (leverantörskedje), GDPR (personuppgiftsbiträdesavtal), kontraktskrav",
                "B2C": "GDPR (primärt), samtycke, rätt till dataportabilitet",
                "skillnad": "B2B omfattas av leverantörskedjekrav i NIS2. B2C har tyngre GDPR-fokus på individrättigheter."
            },
            "viktigaste_skyddsatgarder": {
                "B2B": [
                    "Mutual TLS + API-nyckelrotation",
                    "Leverantörsrevision och exit-management",
                    "End-to-end-kryptering av känslig data",
                    "Detaljerad API-loggning till SIEM"
                ],
                "B2C": [
                    "Robust autentisering (BankID/MFA)",
                    "Strict authorization checks (kund-ID validering)",
                    "Rate limiting + DDoS-skydd",
                    "Input validation mot injection-attacker"
                ]
            }
        }

    def _generera_api_sammanfattning(self, scenarios: List[APIScenario]) -> str:
        """Genererar textsammanfattning för ledningen"""
        b2b_count = sum(1 for s in scenarios if s.typ == APITyp.B2B.value)
        b2c_count = sum(1 for s in scenarios if s.typ == APITyp.B2C.value)

        total_risker = sum(len(s.risker) for s in scenarios)

        return f"""
API-säkerhetsanalys omfattar {len(scenarios)} kritiska scenarios:
- {b2b_count} B2B-integrationer (partners och leverantörer)
- {b2c_count} B2C-tjänster (97 000+ slutanvändare)

Totalt identifierades {total_risker} API-relaterade risker.

Högsta prioritet:
1. B2C: Implementera strikt auktoriseringskontroll för att förhindra IDOR
2. B2B: Automatisera API-nyckelrotation för partners
3. Båda: Utöka API-loggning och anomalidetektering

Regulatorisk påverkan: GDPR Art. 32 (säkerhet) och NIS2 Art. 21 (leverantörskedje).
        """.strip()

    def _identifiera_kritiska_api_risker(self, scenarios: List[APIScenario]) -> List[Dict]:
        """Identifierar de mest kritiska API-riskerna"""
        kritiska = []

        for scenario in scenarios:
            for risk in scenario.risker:
                if risk["sannolikhet"] in ["Hög", "Medel"]:
                    kritiska.append({
                        "scenario": scenario.namn,
                        "typ": scenario.typ,
                        "risk": risk["risk"],
                        "påverkan": risk["påverkan"],
                        "sannolikhet": risk["sannolikhet"]
                    })

        # Sortera: Hög sannolikhet först
        kritiska.sort(key=lambda x: 0 if x["sannolikhet"] == "Hög" else 1)

        return kritiska[:5]  # Top 5

    def _koppla_api_till_regelverk(self, scenarios: List[APIScenario]) -> Dict:
        """Kopplar API-scenarios till regelverk"""
        regelverk_mapping = {}

        for scenario in scenarios:
            for regel in scenario.regelverk:
                if regel not in regelverk_mapping:
                    regelverk_mapping[regel] = []
                regelverk_mapping[regel].append({
                    "scenario": scenario.namn,
                    "typ": scenario.typ
                })

        return regelverk_mapping

    def _scenario_till_dict(self, scenario: APIScenario) -> Dict:
        """Konverterar APIScenario till dictionary för Excel"""
        return {
            "Scenario-ID": scenario.scenario_id,
            "Typ": scenario.typ,
            "Namn": scenario.namn,
            "Beskrivning": scenario.beskrivning,
            "Dataflöde": scenario.dataflöde,
            "Kryptering": scenario.kryptering,
            "Kryptering_detaljer": str(scenario.kryptering_detaljer),
            "Autentisering": ", ".join(scenario.autentisering),
            "Autentisering_detaljer": str(scenario.autentisering_detaljer),
            "Antal_risker": len(scenario.risker),
            "Risker": scenario.risker,
            "Mitigeringar": scenario.mitigeringar,
            "Regelverk": ", ".join(scenario.regelverk),
            "CIS_Controls": ", ".join(scenario.cis_controls),
            "Kommentar": scenario.kommentar
        }