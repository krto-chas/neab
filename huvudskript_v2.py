#!/usr/bin/env python3
"""
NEAB Security Assessment Suite v2.0
Huvudskript för CLI-körning - Kompatibel med befintliga moduler
"""
import sys
import io
from pathlib import Path
from datetime import datetime
import logging

# Fix för Windows konsol encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Lägg till projektets root till Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.input_loader import NEABInputLoader, InputValidator
from utils.console_formatter import ConsoleFormatter, ProgressBar
from utils.pdf_template import create_neab_report

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('neab_assessment.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class NEABSecurityAssessment:
    """Huvudklass för NEAB Security Assessment"""

    def __init__(self, input_file=None):
        """
        Args:
            input_file: Sökväg till input YAML/JSON. Om None används default template.
        """
        # Skapa output-mapp med timestamp
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = project_root / 'data' / 'output' / self.timestamp
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Ladda input
        try:
            self.input_loader = NEABInputLoader(input_file)
            ConsoleFormatter.success(f"Input laddad från: {self.input_loader.input_file}")
        except Exception as e:
            ConsoleFormatter.error(f"Kunde inte ladda input: {e}")
            sys.exit(1)

        # Validera input
        valid, errors = InputValidator.validate_all(self.input_loader.get_all_data())
        if not valid:
            ConsoleFormatter.error("Input-validering misslyckades:")
            for error in errors:
                ConsoleFormatter.bullet(error)
            sys.exit(1)

        # Initiera moduler (lazy loading - skapas vid behov)
        self.regulatorisk_modul = None
        self.risk_workshop = None
        self.api_sakerhet = None
        self.rapport_generator = None

        ConsoleFormatter.info(f"Output-mapp: {self.output_dir}")

    def _init_modules(self):
        """Initiera moduler (lazy loading)"""
        if self.regulatorisk_modul is None:
            try:
                from modules.regulatorisk_modul import RegulatoriskAnalys
                self.regulatorisk_modul = RegulatoriskAnalys(self.input_loader.get_all_data())
            except ImportError as e:
                ConsoleFormatter.warning(f"Kunde inte ladda RegulatoriskAnalys: {e}")
                self.regulatorisk_modul = MockModule("Regulatorisk")

        if self.risk_workshop is None:
            try:
                from modules.risk_workshop_modul import RiskWorkshop
                self.risk_workshop = RiskWorkshop(self.input_loader.get_all_data())
            except ImportError as e:
                ConsoleFormatter.warning(f"Kunde inte ladda RiskWorkshop: {e}")
                self.risk_workshop = MockModule("RiskWorkshop")

        if self.api_sakerhet is None:
            try:
                from modules.api_sakerhet_modul import APISakerhetAnalys
                self.api_sakerhet = APISakerhetAnalys(self.input_loader.get_all_data())
            except ImportError as e:
                ConsoleFormatter.warning(f"Kunde inte ladda APISakerhetAnalys: {e}")
                self.api_sakerhet = MockModule("APISakerhet")

        if self.rapport_generator is None:
            try:
                from modules.rapport_generator import RapportGenerator
                import inspect

                # Inspektera signaturen
                sig = inspect.signature(RapportGenerator.__init__)
                params = list(sig.parameters.keys())

                # Ta bort 'self' från parameterlistan
                if 'self' in params:
                    params.remove('self')

                # Försök initiera baserat på antal parametrar
                if len(params) == 0:
                    self.rapport_generator = RapportGenerator()
                elif len(params) == 1:
                    # Antingen config eller output_dir
                    param_name = params[0]
                    if 'config' in param_name.lower():
                        self.rapport_generator = RapportGenerator(self.input_loader.get_all_data())
                    else:
                        self.rapport_generator = RapportGenerator(str(self.output_dir))
                else:
                    # Två eller fler parametrar - antar config och output_dir
                    self.rapport_generator = RapportGenerator(
                        self.input_loader.get_all_data(),
                        str(self.output_dir)
                    )

                ConsoleFormatter.success(f"RapportGenerator initierad med {len(params)} parametrar")

            except (ImportError, Exception) as e:
                ConsoleFormatter.warning(f"Kunde inte ladda RapportGenerator: {e}")
                self.rapport_generator = MockRapportGenerator(self.output_dir)

    def visa_input_sammanfattning(self):
        """Visa sammanfattning av inläst input"""
        ConsoleFormatter.section("INPUT SAMMANFATTNING")
        print(self.input_loader.get_summary())

    def kor_komplett_analys(self):
        """Genomför komplett säkerhetsanalys"""

        # Visa banner
        ConsoleFormatter.banner()

        # Visa input-sammanfattning
        self.visa_input_sammanfattning()

        # Initiera moduler
        self._init_modules()

        # Huvudanalys
        ConsoleFormatter.header("STARTAR KOMPLETT SÄKERHETSANALYS")

        resultat = {}

        # Steg 1: Regulatorisk kartläggning
        ConsoleFormatter.step(1, 4, "Genomför regulatorisk kartläggning...")
        try:
            # Debug: Visa tillgängliga metoder
            available_methods = [m for m in dir(self.regulatorisk_modul) if not m.startswith('_')]
            logger.info(f"Tillgängliga metoder i RegulatoriskAnalys: {', '.join(available_methods[:10])}")

            # Försök hitta rätt metod
            if hasattr(self.regulatorisk_modul, 'kartlägg_krav'):
                regulatorisk_data = self.regulatorisk_modul.kartlägg_krav()
            elif hasattr(self.regulatorisk_modul, 'genomför_kartläggning'):
                regulatorisk_data = self.regulatorisk_modul.genomför_kartläggning()
            elif hasattr(self.regulatorisk_modul, 'genomför_analys'):
                regulatorisk_data = self.regulatorisk_modul.genomför_analys()
            elif hasattr(self.regulatorisk_modul, 'utför_kartläggning'):
                regulatorisk_data = self.regulatorisk_modul.utför_kartläggning()
            elif hasattr(self.regulatorisk_modul, 'analysera'):
                regulatorisk_data = self.regulatorisk_modul.analysera()
            elif hasattr(self.regulatorisk_modul, 'genomför'):
                regulatorisk_data = self.regulatorisk_modul.genomför()
            else:
                # Försök bara anropa utan argument
                regulatorisk_data = {'krav': [], 'efterlevnad_procent': 0}
                ConsoleFormatter.warning(
                    f"Kunde inte hitta kartläggningsmetod. Tillgängliga: {', '.join([m for m in available_methods if 'genom' in m.lower() or 'analys' in m.lower() or 'kartlägg' in m.lower()][:5])}")

            resultat['regulatorisk'] = regulatorisk_data

            # Beräkna efterlevnad
            krav = regulatorisk_data.get('krav', [])
            if krav:
                uppfyllt = sum(1 for k in krav if k.get('status') == 'Uppfyllt')
                efterlevnad = (uppfyllt / len(krav)) * 100
                regulatorisk_data['efterlevnad_procent'] = efterlevnad
            else:
                regulatorisk_data['efterlevnad_procent'] = 0

            ConsoleFormatter.success(
                f"Identifierade {len(krav)} regulatoriska krav"
            )
            ConsoleFormatter.bullet(
                f"Efterlevnad: {int(round(regulatorisk_data.get('efterlevnad_procent', 0)))}%",
                indent=4
            )
        except Exception as e:
            ConsoleFormatter.error(f"Regulatorisk kartläggning misslyckades: {e}")
            logger.exception("Fel i regulatorisk modul")
            resultat['regulatorisk'] = {'krav': [], 'efterlevnad_procent': 0}

        # Steg 2: Riskanalys
        ConsoleFormatter.step(2, 4, "Genomför riskanalys (MSB-metod + STRIDE)...")
        try:
            # RiskWorkshop kan kräva input_data och regulatorisk_data
            if hasattr(self.risk_workshop, 'genomför_workshop'):
                # Försök med olika signaturer
                import inspect
                sig = inspect.signature(self.risk_workshop.genomför_workshop)
                params = [p for p in sig.parameters.values() if p.name != 'self']

                if len(params) == 0:
                    risk_data = self.risk_workshop.genomför_workshop()
                elif len(params) == 1:
                    # Ett argument - kan vara input_data eller regulatorisk_data
                    if 'regulatorisk' in params[0].name.lower():
                        risk_data = self.risk_workshop.genomför_workshop(resultat.get('regulatorisk', {}))
                    else:
                        risk_data = self.risk_workshop.genomför_workshop(self.input_loader.get_all_data())
                else:
                    # Två eller fler argument - ge både input och regulatorisk
                    risk_data = self.risk_workshop.genomför_workshop(
                        self.input_loader.get_all_data(),
                        resultat.get('regulatorisk', {})
                    )
            else:
                risk_data = {'risker': [], 'riskfordelning': {}}
                ConsoleFormatter.warning("Kunde inte hitta workshop-metod")

            resultat['risk'] = risk_data

            risker = risk_data.get('risker', [])
            ConsoleFormatter.success(
                f"Identifierade {len(risker)} risker"
            )

            # Visa riskfördelning
            risk_distribution = {}
            for risk in risker:
                level = risk.get('risknivå', 'Okänd')
                risk_distribution[level] = risk_distribution.get(level, 0) + 1

            risk_data['riskfordelning'] = risk_distribution

            for level, count in risk_distribution.items():
                if count > 0:
                    ConsoleFormatter.bullet(
                        f"{level}: {count} st",
                        indent=4
                    )
        except Exception as e:
            ConsoleFormatter.error(f"Riskanalys misslyckades: {e}")
            logger.exception("Fel i risk workshop")
            resultat['risk'] = {'risker': [], 'riskfordelning': {}}

        # Steg 3: Mitigeringsstrategier
        ConsoleFormatter.step(3, 4, "Utvecklar mitigeringsstrategier...")
        try:
            # Kan heta generera_atgardsplan eller generera_åtgärdsplan
            if hasattr(self.risk_workshop, 'generera_åtgärdsplan'):
                # Kolla signaturen
                import inspect
                sig = inspect.signature(self.risk_workshop.generera_åtgärdsplan)
                params = [p for p in sig.parameters.values() if p.name != 'self']

                if len(params) == 1:
                    # Ett argument - antingen risk_data eller regulatorisk_data
                    if 'risk' in params[0].name.lower():
                        mitigering_data = self.risk_workshop.generera_åtgärdsplan(resultat.get('risk', {}))
                    else:
                        mitigering_data = self.risk_workshop.generera_åtgärdsplan(resultat.get('regulatorisk', {}))
                else:
                    # Två argument - både risk och regulatorisk
                    mitigering_data = self.risk_workshop.generera_åtgärdsplan(
                        resultat.get('risk', {}),
                        resultat.get('regulatorisk', {})
                    )
            elif hasattr(self.risk_workshop, 'generera_atgardsplan'):
                mitigering_data = self.risk_workshop.generera_atgardsplan(resultat.get('risk', {}))
            else:
                mitigering_data = {'åtgärder': []}
                ConsoleFormatter.warning("Kunde inte hitta åtgärdsplan-metod")

            resultat['mitigering'] = mitigering_data

            ConsoleFormatter.success(
                f"Genererade {len(mitigering_data.get('åtgärder', []))} åtgärder"
            )
        except Exception as e:
            ConsoleFormatter.error(f"Mitigering misslyckades: {e}")
            logger.exception("Fel i mitigering")
            resultat['mitigering'] = {'åtgärder': []}

        # Steg 4: API-säkerhet
        ConsoleFormatter.step(4, 4, "Analyserar API-säkerhet (B2B/B2C)...")
        try:
            # Kan heta analysera, genomför_analys eller liknande
            if hasattr(self.api_sakerhet, 'analysera'):
                api_data = self.api_sakerhet.analysera()
            elif hasattr(self.api_sakerhet, 'genomför_analys'):
                api_data = self.api_sakerhet.genomför_analys()
            elif hasattr(self.api_sakerhet, 'analysera_scenarios'):
                api_data = self.api_sakerhet.analysera_scenarios(
                    self.input_loader.get_api_scenarios()
                )
            else:
                api_data = {'scenarios': []}
                ConsoleFormatter.warning("Kunde inte hitta API-analys-metod")

            resultat['api'] = api_data

            ConsoleFormatter.success(
                f"Analyserade {len(api_data.get('scenarios', []))} API-scenarios"
            )
        except Exception as e:
            ConsoleFormatter.error(f"API-analys misslyckades: {e}")
            logger.exception("Fel i API-analys")
            resultat['api'] = {'scenarios': []}

        # Generera risk heat map
        ConsoleFormatter.info("Genererar risk heat map...")
        try:
            from utils.risk_heatmap import generate_risk_heatmap

            risker = resultat.get('risk', {}).get('risker', [])
            logger.info(f"Antal risker för heat map: {len(risker)}")

            if risker:
                heatmap_path = self.output_dir / f"NEAB_Risk_Heatmap_{self.timestamp}.png"
                logger.info(f"Skapar heat map: {heatmap_path}")
                generate_risk_heatmap(risker, heatmap_path)
                resultat['heatmap_path'] = str(heatmap_path)
                ConsoleFormatter.success(f"Heat map skapad: {heatmap_path.name}")
            else:
                ConsoleFormatter.warning("Ingen heat map skapad (inga risker)")
                logger.warning("Risklista är tom")
        except ImportError as e:
            ConsoleFormatter.warning(f"Kunde inte importera heat map-modul: {e}")
            logger.exception("Heat map import-fel")
        except Exception as e:
            ConsoleFormatter.warning(f"Kunde inte skapa heat map: {e}")
            logger.exception("Heat map-fel")

        # Generera rapporter
        ConsoleFormatter.section("GENERERAR RAPPORTER")

        progress = ProgressBar(4, "Skapar filer")

        try:
            # Excel - försök flera strategier
            excel_path = None

            # Strategi 1: Använd generera_komplett_paket om den finns
            if hasattr(self.rapport_generator, 'generera_komplett_paket'):
                try:
                    logger.info("Försöker generera_komplett_paket...")
                    paket = self.rapport_generator.generera_komplett_paket(resultat)

                    if isinstance(paket, dict):
                        excel_path = paket.get('excel_path')
                        if excel_path and isinstance(excel_path, str):
                            excel_path = Path(excel_path)

                    logger.info(f"generera_komplett_paket returnerade: {type(paket)}")

                except Exception as e:
                    logger.warning(f"generera_komplett_paket misslyckades: {e}")

            # Strategi 2: Leta efter befintlig Excel-fil
            if not excel_path or not excel_path.exists():
                logger.info("Letar efter Excel-fil i output-mappen...")
                for f in self.output_dir.glob('*.xlsx'):
                    excel_path = f
                    logger.info(f"Hittade Excel: {f}")
                    break

            # Strategi 3: Skapa Excel med fullständig backup-generator
            if not excel_path or not excel_path.exists():
                logger.info("Skapar Excel med backup-generator...")
                try:
                    from utils.excel_backup_generator import generate_excel_backup

                    excel_path = self.output_dir / f"NEAB_Sakerhetsanalys_{self.timestamp}.xlsx"
                    generate_excel_backup(resultat, excel_path)
                    logger.info(f"Backup Excel skapad: {excel_path}")

                except Exception as e2:
                    logger.error(f"Backup Excel misslyckades: {e2}")
                    logger.exception("Excel backup-fel")

            progress.update()
            if excel_path and excel_path.exists():
                ConsoleFormatter.progress_complete("Excel-fil skapad", excel_path)
            else:
                ConsoleFormatter.warning("Excel-fil kunde inte skapas")

        except Exception as e:
            ConsoleFormatter.warning(f"Excel-generering misslyckades: {e}")
            logger.exception("Excel-fel")
            progress.update()

        try:
            # PDF - använd data från JSON för att säkerställa fullständighet
            pdf_path = self.output_dir / f"NEAB_Ledningsrapport_{self.timestamp}.pdf"

            # Läs JSON för fullständig data
            if hasattr(self, 'json_path') and self.json_path.exists():
                import json
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    full_resultat = json.load(f)
                pdf_data = self._prepare_pdf_data(full_resultat)
            else:
                pdf_data = self._prepare_pdf_data(resultat)

            # Skapa ny PDF med förbättrad mall och fullständig data
            create_neab_report(pdf_path, pdf_data)

            progress.update()
            ConsoleFormatter.progress_complete("PDF-rapport skapad", pdf_path)
        except Exception as e:
            ConsoleFormatter.warning(f"PDF-generering misslyckades: {e}")
            logger.exception("PDF-fel")
            # Kolla om PDF finns ändå
            pdf_files = list(self.output_dir.glob('*.pdf'))
            if pdf_files:
                ConsoleFormatter.info(f"Men PDF-fil hittades: {pdf_files[0].name}")
            progress.update()

        try:
            # JSON
            if hasattr(self.rapport_generator, 'generera_json'):
                json_path = self.rapport_generator.generera_json(resultat)
            elif hasattr(self.rapport_generator, 'spara_json'):
                json_path = self.rapport_generator.spara_json(resultat)
            else:
                # Spara manuellt
                import json
                json_path = self.output_dir / f"NEAB_Resultat_{self.timestamp}.json"
                json_path.write_text(json.dumps(resultat, indent=2, ensure_ascii=False), encoding='utf-8')

            progress.update()
            ConsoleFormatter.progress_complete("JSON-data skapad", json_path)

            # Spara även JSON-path för senare användning
            self.json_path = json_path
        except Exception as e:
            ConsoleFormatter.warning(f"JSON-generering misslyckades: {e}")
            progress.update()

        try:
            # Protokoll - kolla först om vi har JSON-data att använda
            if hasattr(self, 'json_path') and self.json_path.exists():
                # Läs JSON för att få fullständig data
                import json
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    full_resultat = json.load(f)
            else:
                full_resultat = resultat

            protokoll_path = self.output_dir / f"Workshop_Protokoll_{self.timestamp}.txt"

            # Skapa detaljerat protokoll med data från JSON
            reg_krav = full_resultat.get('regulatorisk', {}).get('krav', [])
            risker = full_resultat.get('risk', {}).get('risker', [])
            atgarder = full_resultat.get('mitigering', {}).get('åtgärder', [])

            protokoll_text = f"""RISKWORKSHOP - PROTOKOLL
================================================================================
Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Organisation: {self.input_loader.get_organisation_data().get('namn', 'Nordlunda Energi AB')}
Deltagare: CISO, IT-chef, Driftchef, OT-säkerhetsansvarig

AGENDA:
1. Genomgång av regulatoriska krav
2. Identifiering av tillgångar och beroenden
3. Hotmodellering med STRIDE
4. Konsekvens- och sannolikhetsbedömning
5. Rangordning av risker
6. Diskussion av mitigeringsstrategier

RESULTAT:
- Identifierade {len(risker)} risker
- Kartlagda {len(reg_krav)} regulatoriska krav
- Föreslagna {len(atgarder)} åtgärder

Workshopen genomfördes enligt MSB:s metodstöd med STRIDE för hotmodellering.
"""
            protokoll_path.write_text(protokoll_text, encoding='utf-8')

            progress.update()
            ConsoleFormatter.progress_complete("Workshop-protokoll skapat", protokoll_path)
        except Exception as e:
            ConsoleFormatter.warning(f"Protokoll-generering misslyckades: {e}")
            progress.update()

        progress.complete()

        # Slutsammanfattning
        self._visa_slutsammanfattning(resultat)

        return resultat

    def _prepare_pdf_data(self, resultat):
        """Förbered data för PDF-generering"""
        # Debug: Logga strukturen
        logger.info("=== DEBUG: Förbereder PDF-data ===")
        logger.info(f"Resultat nycklar: {list(resultat.keys())}")

        org_data = self.input_loader.get_organisation_data()
        reg_data = resultat.get('regulatorisk', {})
        risk_data = resultat.get('risk', {})
        mitigering_data = resultat.get('mitigering', {})

        logger.info(f"Regulatorisk nycklar: {list(reg_data.keys())}")
        logger.info(f"Risk nycklar: {list(risk_data.keys())}")
        logger.info(f"Mitigering nycklar: {list(mitigering_data.keys())}")

        # Hämta krav med olika möjliga nycklar
        krav = reg_data.get('krav', reg_data.get('requirements', []))
        logger.info(f"Antal krav: {len(krav)}")
        if krav:
            logger.info(f"Exempel krav struktur: {list(krav[0].keys()) if krav else 'Tom lista'}")

        # Hämta risker med olika möjliga nycklar
        risker = risk_data.get('risker', risk_data.get('risks', []))
        logger.info(f"Antal risker: {len(risker)}")
        if risker:
            logger.info(
                f"Exempel risk struktur: {list(risker[0].keys()) if isinstance(risker[0], dict) else 'Inte dict'}")
            logger.info(f"Första risken: {risker[0]}")

        # Samla top risker
        top_risks = []

        # Sortera efter risknivå om möjligt
        try:
            # Försök sortera efter risknivå
            risk_order = {'Mycket hög': 0, 'Hög': 1, 'Medel': 2, 'Låg': 3, 'Okänd': 99}
            sorterade_risker = sorted(
                risker,
                key=lambda r: risk_order.get(
                    r.get('Risknivå', r.get('risknivå', r.get('riskniva', r.get('risk_level', 'Okänd')))),
                    99
                )
            )

            for risk in sorterade_risker[:5]:
                # Prova olika nycklar - både versaler och gemener
                hot = (risk.get('Hot') or risk.get('hot') or risk.get('threat') or
                       risk.get('beskrivning') or risk.get('Beskrivning') or
                       risk.get('description') or 'Okänt hot')

                tillgang = (risk.get('Tillgång / område') or risk.get('Tillgång') or
                            risk.get('tillgång') or risk.get('tillgang') or
                            risk.get('asset') or 'Okänd tillgång')

                riskniva = (risk.get('Risknivå') or risk.get('risknivå') or
                            risk.get('riskniva') or risk.get('risk_level') or 'Okänd')

                risk_str = f"{hot} ({tillgang}) - {riskniva}"
                top_risks.append(risk_str)
                logger.info(f"Top risk: {risk_str}")
        except Exception as e:
            logger.warning(f"Kunde inte sortera risker: {e}")
            # Fallback - ta bara första 5
            for i, risk in enumerate(risker[:5]):
                logger.info(f"Fallback risk {i}: {risk}")
                if isinstance(risk, dict):
                    hot = list(risk.values())[0] if risk else 'N/A'
                    risk_str = f"{hot}"
                else:
                    risk_str = str(risk)
                top_risks.append(risk_str)

        logger.info(f"Top risks slutresultat: {top_risks}")

        # Samla regulatoriska brister
        regulatory_gaps = []

        for krav_item in krav:
            status = (krav_item.get('Status') or krav_item.get('status') or
                      krav_item.get('efterlevnad') or krav_item.get('compliance') or '')
            if status in ['Delvis uppfyllt', 'Ej uppfyllt', 'Delvis', 'Ej', 'Partially Compliant', 'Non-Compliant']:
                beskrivning = (krav_item.get('Krav') or krav_item.get('krav_beskrivning') or
                               krav_item.get('krav') or krav_item.get('requirement') or 'Okänt krav')
                regelverk = (krav_item.get('Regelverk') or krav_item.get('regelverk') or
                             krav_item.get('standard') or krav_item.get('framework') or 'Okänt')
                gap_str = f"{beskrivning} ({regelverk})"
                regulatory_gaps.append(gap_str)

        logger.info(f"Regulatory gaps: {len(regulatory_gaps)}")

        # Samla prioriterade åtgärder
        priority_actions = []
        seen_actions = set()  # För att undvika dubbletter
        atgarder = mitigering_data.get('åtgärder', mitigering_data.get('atgarder', mitigering_data.get('actions', [])))

        logger.info(f"Antal åtgärder: {len(atgarder)}")
        if atgarder:
            logger.info(f"Exempel åtgärd: {atgarder[0]}")

        for i, action in enumerate(atgarder):
            logger.info(f"Bearbetar åtgärd {i + 1}: {action if not isinstance(action, dict) else list(action.keys())}")
            if isinstance(action, dict):
                action_str = (action.get('Beskrivning') or
                              action.get('beskrivning') or
                              action.get('föreslagen_åtgärd') or
                              action.get('atgard') or
                              action.get('action') or 'Okänd åtgärd')
            else:
                action_str = str(action)

            # Lägg bara till om inte duplikat
            if action_str not in seen_actions:
                priority_actions.append(action_str)
                seen_actions.add(action_str)
                logger.info(f"Åtgärd {len(priority_actions)} tillagd: {action_str[:80]}...")
            else:
                logger.info(f"Åtgärd {i + 1} är duplikat, skippar")

            # Sluta när vi har 5 unika
            if len(priority_actions) >= 5:
                break

        logger.info(f"Priority actions: {priority_actions}")

        # Riskfördelning
        risk_distribution = risk_data.get('riskfordelning',
                                          risk_data.get('fordelning', risk_data.get('distribution', {})))

        # Om riskfördelning bara har 'Okänd', beräkna från riskerna
        if risk_distribution.get('Okänd', 0) == len(risker) and risker:
            logger.info("Riskfördelning visar alla som 'Okänd', räknar om från risker...")
            risk_distribution = {}
            for risk in risker:
                level = (risk.get('Risknivå') or risk.get('risknivå') or
                         risk.get('riskniva') or risk.get('risk_level') or 'Okänd')
                risk_distribution[level] = risk_distribution.get(level, 0) + 1
            logger.info(f"Ny riskfördelning: {risk_distribution}")

        logger.info(f"Risk distribution: {risk_distribution}")

        # Beräkna compliance rate
        compliance_rate = reg_data.get('efterlevnad_procent', reg_data.get('compliance_rate', 0))
        if compliance_rate == 0 and krav:
            uppfyllt = sum(1 for k in krav if k.get('Status', k.get('status', '')) == 'Uppfyllt')
            compliance_rate = (uppfyllt / len(krav)) * 100
            # Uppdatera resultat med rätt värde
            resultat['regulatorisk']['efterlevnad_procent'] = compliance_rate

        # Antal uppfyllda krav
        fulfilled = sum(1 for k in krav if k.get('Status', k.get('status', '')) == 'Uppfyllt')
        partial = sum(1 for k in krav if k.get('Status', k.get('status', '')) in ['Delvis uppfyllt', 'Delvis'])
        not_fulfilled = sum(1 for k in krav if k.get('Status', k.get('status', '')) in ['Ej uppfyllt', 'Ej'])

        pdf_data = {
            'organisation': org_data.get('namn', 'Nordlunda Energi AB'),
            'compliance_rate': compliance_rate,
            'very_high_risks': risk_distribution.get('Mycket hög', 0),
            'high_risks': risk_distribution.get('Hög', 0),
            'critical_actions': len(priority_actions),
            'top_risks': top_risks if top_risks else ['Ingen data tillgänglig'],
            'regulatory_gaps': regulatory_gaps if regulatory_gaps else ['Ingen data tillgänglig'],
            'priority_actions': priority_actions if priority_actions else ['Ingen data tillgänglig'],
            'total_requirements': len(krav),
            'fulfilled': fulfilled,
            'partial': partial,
            'not_fulfilled': not_fulfilled,
            'risk_distribution': risk_distribution,
            'heatmap_path': resultat.get('heatmap_path'),  # Lägg till heat map path
            'priority_areas': [
                'Styrelseutbildning (NIS2)',
                'DPIA för mätdata (GDPR)',
                'Formalisering av riskhanteringsprocesser'
            ],
            'core_business': (
                f"{org_data.get('namn', 'NEAB')} är ett {org_data.get('typ', 'energibolag')} "
                f"som betjänar ca {org_data.get('kunder', {}).get('elnat', 0):,} elnätskunder "
                f"och {org_data.get('kunder', {}).get('fjarrvärme', 0):,} fjärrvärmekunder."
            ),
            'critical_systems': (
                "SCADA/DCS för styrning, AMI för mätdata, OMS för avbrottshantering, "
                "samt kund- och faktureringssystem."
            ),
            'security_governance': (
                "CISO med stab, OT-säkerhetsansvarig, samt SOC via MSSP med 24/7-övervakning."
            ),
            'follow_up_plan': (
                "Säkerhetsarbetet följs upp kvartalsvis med rapportering till styrelsen. "
                "Riskanalys uppdateras årligen eller vid väsentliga förändringar. "
                "Åtgärder spåras i riskregister med ansvariga och deadlines."
            )
        }

        logger.info(f"=== PDF data sammanfattning ===")
        logger.info(f"Compliance: {compliance_rate}%")
        logger.info(f"Mycket höga risker: {pdf_data['very_high_risks']}")
        logger.info(f"Top risks antal: {len(pdf_data['top_risks'])}")
        logger.info(f"Priority actions antal: {len(pdf_data['priority_actions'])}")

        return pdf_data

    def _visa_slutsammanfattning(self, resultat):
        """Visa slutsammanfattning i konsolen"""
        ConsoleFormatter.header("ANALYS SLUTFÖRD")

        reg_data = resultat.get('regulatorisk', {})
        risk_data = resultat.get('risk', {})

        # Beräkna korrekt riskfördelning från riskerna själva
        risker = risk_data.get('risker', [])
        actual_distribution = {}
        if risker:
            for risk in risker:
                level = (risk.get('Risknivå') or risk.get('risknivå') or
                         risk.get('riskniva') or 'Okänd')
                actual_distribution[level] = actual_distribution.get(level, 0) + 1

        # Beräkna korrekt compliance från krav
        krav = reg_data.get('krav', [])
        compliance_rate = 0
        if krav:
            uppfyllt = sum(1 for k in krav if k.get('Status', k.get('status', '')) == 'Uppfyllt')
            compliance_rate = (uppfyllt / len(krav)) * 100

        summary_data = {
            'Regelefterlevnad': f"{int(round(compliance_rate))}%",
            'Totalt risker': str(len(risker)),
            'Mycket höga risker': str(actual_distribution.get('Mycket hög', 0)),
            'Höga risker': str(actual_distribution.get('Hög', 0)),
            'Åtgärder identifierade': str(len(resultat.get('mitigering', {}).get('åtgärder', []))),
            'Output-mapp': str(self.output_dir)
        }

        ConsoleFormatter.summary_box("RESULTAT", summary_data)

        # Lista genererade filer
        ConsoleFormatter.info("Genererade filer:")
        for file in sorted(self.output_dir.glob('*')):
            ConsoleFormatter.bullet(file.name, indent=2)


class MockModule:
    """Mock-modul för att hantera saknade moduler"""

    def __init__(self, name):
        self.name = name

    def genomför_kartläggning(self):
        return {'krav': [], 'efterlevnad_procent': 0}

    def genomför_workshop(self):
        return {'risker': [], 'riskfordelning': {}}

    def generera_atgardsplan(self, risk_data):
        return {'åtgärder': []}

    def analysera(self):
        return {'scenarios': []}


class MockRapportGenerator:
    """Mock för rapport-generator"""

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    def generera_excel(self, resultat):
        path = self.output_dir / "mock_excel.txt"
        path.write_text("Mock Excel - modulen kunde inte laddas")
        return path

    def generera_docx(self, resultat):
        path = self.output_dir / "mock_excel.txt"
        path.write_text("Mock Excel - modulen kunde inte laddas")
        return path

    def generera_json(self, resultat):
        import json
        path = self.output_dir / "mock_results.json"
        path.write_text(json.dumps(resultat, indent=2, ensure_ascii=False))
        return path

    def generera_protokoll(self, resultat):
        path = self.output_dir / "mock_protokoll.txt"
        path.write_text("Mock Protokoll - modulen kunde inte laddas")
        return path


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='NEAB Security Assessment Suite v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exempel:
  # Använd default template
  python huvudskript.py

  # Använd egen input-fil
  python huvudskript.py -i min_input.yaml

  # Visa endast input-sammanfattning
  python huvudskript.py -i min_input.yaml --show-input
        """
    )

    parser.add_argument(
        '-i', '--input',
        help='Sökväg till input YAML/JSON fil',
        default=None
    )

    parser.add_argument(
        '--show-input',
        action='store_true',
        help='Visa endast input-sammanfattning och avsluta'
    )

    args = parser.parse_args()

    try:
        # Skapa assessment
        assessment = NEABSecurityAssessment(args.input)

        if args.show_input:
            # Visa bara input och avsluta
            assessment.visa_input_sammanfattning()
            return

        # Kör full analys
        resultat = assessment.kor_komplett_analys()

        ConsoleFormatter.success("Alla operationer slutförda!")

    except KeyboardInterrupt:
        ConsoleFormatter.warning("\nAvbruten av användare")
        sys.exit(130)
    except Exception as e:
        ConsoleFormatter.error(f"Fel uppstod: {e}")
        logger.exception("Oväntad exception")
        sys.exit(1)


if __name__ == "__main__":
    main()