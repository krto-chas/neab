"""
Professionell PDF-template för NEAB ledningsrapporter
Modern design med färgschema och strukturerad layout
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class NEABPDFTemplate:
    """Professionell PDF-template för NEAB-rapporter"""

    # NEAB Färgschema (energibolag - blå/grön)
    COLORS = {
        'primary': HexColor('#1e3a8a'),      # Mörk blå (pålitlighet)
        'secondary': HexColor('#3b82f6'),    # Ljus blå (teknologi)
        'accent': HexColor('#10b981'),       # Grön (energi/hållbarhet)
        'success': HexColor('#10b981'),      # Grön
        'warning': HexColor('#f59e0b'),      # Orange
        'danger': HexColor('#ef4444'),       # Röd
        'neutral': HexColor('#6b7280'),      # Grå
        'light_gray': HexColor('#f3f4f6'),   # Ljusgrå bakgrund
        'dark_gray': HexColor('#374151')     # Mörkgrå text
    }

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2.5*cm,
            title="NEAB Säkerhetsrapport",
            author="NEAB Security Assessment Suite"
        )
        self.story = []
        self.styles = self._create_styles()
        self.width, self.height = A4

    def _create_styles(self):
        """Skapar anpassade textstilar"""
        styles = getSampleStyleSheet()

        # Huvudtitel (försättssida)
        styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=self.COLORS['primary'],
            spaceAfter=20,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=34
        ))

        # Undertitel (försättssida)
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=self.COLORS['secondary'],
            spaceAfter=40,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Organisation (försättssida)
        styles.add(ParagraphStyle(
            name='CoverOrg',
            parent=styles['Normal'],
            fontSize=20,
            textColor=self.COLORS['primary'],
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Rubrik 1
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=self.COLORS['primary'],
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderPadding=5,
            leftIndent=0,
            borderWidth=0,
            borderColor=self.COLORS['primary']
        ))

        # Rubrik 2
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.COLORS['secondary'],
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))

        # Rubrik 3
        styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=self.COLORS['dark_gray'],
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Brödtext
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            textColor=self.COLORS['dark_gray']
        ))

        # Bullet points
        styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=styles['BodyText'],
            fontSize=10,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=5,
            textColor=self.COLORS['dark_gray'],
            bulletFontName='Helvetica',
            bulletFontSize=10
        ))

        # Highlight box
        styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=self.COLORS['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=10
        ))

        # Fotnoter
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=self.COLORS['neutral'],
            alignment=TA_CENTER
        ))

        return styles

    def _header_footer(self, canvas_obj, doc):
        """Lägg till header och footer på varje sida (utom försättssida)"""
        canvas_obj.saveState()

        # Header (efter första sidan)
        if doc.page > 1:
            canvas_obj.setStrokeColor(self.COLORS['primary'])
            canvas_obj.setLineWidth(0.5)
            canvas_obj.line(2*cm, self.height - 2*cm, self.width - 2*cm, self.height - 2*cm)

            canvas_obj.setFont('Helvetica', 9)
            canvas_obj.setFillColor(self.COLORS['neutral'])
            canvas_obj.drawString(2*cm, self.height - 1.7*cm, "NEAB Säkerhetsrapport")
            canvas_obj.drawRightString(self.width - 2*cm, self.height - 1.7*cm,
                                      datetime.now().strftime('%Y-%m-%d'))

        # Footer
        canvas_obj.setStrokeColor(self.COLORS['primary'])
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(2*cm, 2*cm, self.width - 2*cm, 2*cm)

        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(self.COLORS['neutral'])
        canvas_obj.drawCentredString(self.width / 2, 1.5*cm,
                                    f"Sida {doc.page}")
        canvas_obj.drawString(2*cm, 1.5*cm, "Nordlunda Energi AB")
        canvas_obj.drawRightString(self.width - 2*cm, 1.5*cm, "Konfidentiellt")

        canvas_obj.restoreState()

    def add_cover_page(self, data):
        """Skapar professionell försättssida"""
        # Spacer från toppen
        self.story.append(Spacer(1, 2*cm))

        # Titel med bakgrund
        self.story.append(Paragraph(
            "Riskworkshop med regulatorisk<br/>kartläggning",
            self.styles['CoverTitle']
        ))

        self.story.append(Spacer(1, 1*cm))

        # Organisation
        self.story.append(Paragraph(
            data.get('organisation', 'Nordlunda Energi AB'),
            self.styles['CoverOrg']
        ))

        self.story.append(Spacer(1, 3*cm))

        # Status-översikt i box
        status_items = [
            f"Regelefterlevnad: {int(round(data.get('compliance_rate', 0)))}%",
            f"Mycket höga risker: {data.get('very_high_risks', 0)}",
            f"Höga risker: {data.get('high_risks', 0)}",
            f"Kritiska åtgärder: {data.get('critical_actions', 0)}"
        ]

        status_table_data = [[item] for item in status_items]
        status_table = Table(status_table_data, colWidths=[12*cm])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['light_gray']),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLORS['dark_gray']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('LINEABOVE', (0, 0), (-1, 0), 2, self.COLORS['primary']),
            ('LINEBELOW', (0, -1), (-1, -1), 2, self.COLORS['primary']),
        ]))

        self.story.append(status_table)
        self.story.append(Spacer(1, 2*cm))

        # Datum och metadata
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Footer'],
            fontSize=10,
            alignment=TA_CENTER
        )
        self.story.append(Paragraph(
            f"<b>Genererad:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>"
            f"<b>Version:</b> 2.0",
            date_style
        ))

        self.story.append(PageBreak())

    def add_executive_summary(self, data):
        """Lägg till sammanfattning för ledningen"""
        self.story.append(PageBreak())

        self.story.append(Paragraph("Sammanfattning för ledningsnivå",
                                   self.styles['CustomHeading1']))

        # Övergripande bedömning
        self.story.append(Paragraph("Övergripande bedömning:",
                                   self.styles['CustomHeading3']))

        assessment = (f"NEAB har en {int(round(data.get('compliance_rate', 0)))}% regelefterlevnad med "
                     f"{data.get('very_high_risks', 0)} mycket höga och "
                     f"{data.get('high_risks', 0)} höga risker identifierade.")
        self.story.append(Paragraph(assessment, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.3*cm))

        # Viktigaste riskområden
        self.story.append(Paragraph("Viktigaste riskområden:",
                                   self.styles['CustomHeading3']))

        risk_data = []
        for risk in data.get('top_risks', [])[:5]:
            risk_data.append([
                Paragraph("•", self.styles['CustomBody']),
                Paragraph(risk, self.styles['CustomBody'])
            ])

        if risk_data:
            risk_table = Table(risk_data, colWidths=[0.8*cm, 16.2*cm])
            risk_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            self.story.append(risk_table)

        self.story.append(Spacer(1, 0.3*cm))

        # Regulatoriska brister
        self.story.append(Paragraph("Regulatoriska brister:",
                                   self.styles['CustomHeading3']))

        gap_data = []
        for gap in data.get('regulatory_gaps', [])[:5]:
            gap_data.append([
                Paragraph("•", self.styles['CustomBody']),
                Paragraph(gap, self.styles['CustomBody'])
            ])

        if gap_data:
            gap_table = Table(gap_data, colWidths=[0.8*cm, 16.2*cm])
            gap_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            self.story.append(gap_table)

        self.story.append(Spacer(1, 0.3*cm))

        # Föreslagna åtgärder
        self.story.append(Paragraph("Föreslagna prioriterade åtgärder:",
                                   self.styles['CustomHeading3']))

        action_data = []
        for i, action in enumerate(data.get('priority_actions', [])[:5], 1):
            action_data.append([
                Paragraph(f"{i}.", self.styles['CustomBody']),
                Paragraph(action, self.styles['CustomBody'])
            ])

        if action_data:
            action_table = Table(action_data, colWidths=[1*cm, 16*cm])
            action_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            self.story.append(action_table)

        self.story.append(Spacer(1, 0.5*cm))

    def add_organization_section(self, data):
        """Lägg till organisationsbeskrivning"""

        self.story.append(PageBreak())
        self.story.append(Paragraph("Organisationen och kritiska processer",
                                   self.styles['CustomHeading1']))

        # Kärnverksamhet
        self.story.append(Paragraph("Kärnverksamhet:", self.styles['CustomHeading3']))
        core_business = data.get('core_business',
                                'Nordlunda Energi AB är ett regionalt energibolag som driver '
                                'elnätsverksamhet (DSO) och fjärrvärme. Bolaget betjänar ca 85000 '
                                'elnätskunder och 12000 fjärrvärmekunder.')
        self.story.append(Paragraph(core_business, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.3*cm))

        # Kritiska system
        self.story.append(Paragraph("Kritiska system:", self.styles['CustomHeading3']))
        critical_systems = data.get('critical_systems',
                                   'SCADA/DCS för styrning, AMI för mätdata, OMS för avbrottshantering, '
                                   'samt kund- och faktureringssystem.')
        self.story.append(Paragraph(critical_systems, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.3*cm))

        # Säkerhetsstyrning
        self.story.append(Paragraph("Säkerhetsstyrning:", self.styles['CustomHeading3']))
        security_gov = data.get('security_governance',
                               'CISO med stab, OT-säkerhetsansvarig, samt SOC via MSSP '
                               'med 24/7-övervakning.')
        self.story.append(Paragraph(security_gov, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.5*cm))

    def add_regulatory_summary(self, data):
        """Lägg till regulatorisk sammanfattning"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Regulatorisk kartläggning",
                                   self.styles['CustomHeading1']))

        total_reqs = data.get('total_requirements', 9)
        fulfilled = data.get('fulfilled', 2)
        partial = data.get('partial', 6)
        not_fulfilled = data.get('not_fulfilled', 1)
        compliance_rate = data.get('compliance_rate', 55.6)

        summary = (f"Nordlunda Energi AB har en otillräcklig efterlevnadsnivå ({int(round(compliance_rate))}%) "
                  f"av tillämpliga regelverk. Av {total_reqs} identifierade krav: "
                  f"- {fulfilled} fullt uppfyllda "
                  f"- {partial} delvis uppfyllda "
                  f"- {not_fulfilled} ej uppfyllda")

        self.story.append(Paragraph(summary, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.3*cm))

        # Prioriterade områden
        self.story.append(Paragraph("Prioriterade områden för förbättring:",
                                   self.styles['CustomHeading3']))
        priorities = data.get('priority_areas',
                            ['Styrelseutbildning (NIS2)',
                             'DPIA för mätdata (GDPR)',
                             'Formalisering av riskhanteringsprocesser'])

        priority_data = []
        for priority in priorities:
            priority_data.append([
                Paragraph("•", self.styles['CustomBody']),
                Paragraph(priority, self.styles['CustomBody'])
            ])

        if priority_data:
            priority_table = Table(priority_data, colWidths=[0.8*cm, 16.2*cm])
            priority_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            self.story.append(priority_table)

        self.story.append(Spacer(1, 0.5*cm))

    def add_risk_summary(self, data):
        """Lägg till risksammanfattning"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Sammanfattning av riskanalys",
                                   self.styles['CustomHeading1']))

        risks = data.get('risk_distribution', {})
        total = sum(risks.values())

        summary = (f"Riskworkshop identifierade {total} risker: "
                  f"- {risks.get('Mycket hög', 0)} mycket höga risker (kräver omedelbar åtgärd) "
                  f"- {risks.get('Hög', 0)} höga risker (prioriterad hantering) "
                  f"- {risks.get('Medel', 0)} medelhöga risker (planerad hantering) "
                  f"- {risks.get('Låg', 0)} låga risker (övervakning)")

        self.story.append(Paragraph(summary, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.3*cm))

        # Top risker
        self.story.append(Paragraph("Top 3 risker:", self.styles['CustomHeading3']))

        top_risk_data = []
        for i, risk in enumerate(data.get('top_risks', [])[:3], 1):
            top_risk_data.append([
                Paragraph(f"{i}.", self.styles['CustomBody']),
                Paragraph(risk, self.styles['CustomBody'])
            ])

        if top_risk_data:
            top_risk_table = Table(top_risk_data, colWidths=[1*cm, 16*cm])
            top_risk_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            self.story.append(top_risk_table)

        self.story.append(Spacer(1, 0.5*cm))

        # Lägg till heat map om den finns
        heatmap_path = data.get('heatmap_path')
        if heatmap_path and Path(heatmap_path).exists():
            self.story.append(Paragraph("Riskmatris - Visuell översikt:",
                                       self.styles['CustomHeading3']))
            self.story.append(Spacer(1, 0.2*cm))

            # Lägg till bilden
            try:
                img = Image(heatmap_path)
                # Skala till att passa på sidan (max 15cm bred)
                img_width = 15*cm
                aspect = img.imageHeight / img.imageWidth
                img_height = img_width * aspect

                # Begränsa höjd om för hög
                if img_height > 12*cm:
                    img_height = 12*cm
                    img_width = img_height / aspect

                img.drawWidth = img_width
                img.drawHeight = img_height

                self.story.append(img)
                self.story.append(Spacer(1, 0.3*cm))
            except Exception as e:
                logger.warning(f"Kunde inte lägga till heat map i PDF: {e}")

        self.story.append(Spacer(1, 0.2*cm))

    def add_mitigation_summary(self, data):
        """Lägg till mitigeringssammanfattning"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Mitigeringsstrategier och rekommenderade åtgärder",
                                   self.styles['CustomHeading1']))

        priority_actions = data.get('priority_actions', [])
        num_actions = len(priority_actions)

        self.story.append(Paragraph(f"Identifierade {num_actions} prioriterade åtgärder",
                                   self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.3*cm))

        # Lista åtgärder om de finns
        if priority_actions and priority_actions[0] != 'Okänd åtgärd':
            self.story.append(Paragraph("Top prioriterade åtgärder:",
                                       self.styles['CustomHeading3']))

            mitigation_data = []
            for i, action in enumerate(priority_actions[:5], 1):
                # Begränsa längd för läsbarhet
                action_text = action if len(action) < 150 else action[:147] + "..."
                mitigation_data.append([
                    Paragraph(f"{i}.", self.styles['CustomBody']),
                    Paragraph(action_text, self.styles['CustomBody'])
                ])

            if mitigation_data:
                mitigation_table = Table(mitigation_data, colWidths=[1*cm, 16*cm])
                mitigation_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                self.story.append(mitigation_table)

            self.story.append(Spacer(1, 0.3*cm))

        self.story.append(Spacer(1, 0.2*cm))

    def add_follow_up_plan(self, data):
        """Lägg till uppföljningsplan"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Plan för uppföljning och förbättring",
                                   self.styles['CustomHeading1']))

        plan = data.get('follow_up_plan',
                       'Säkerhetsarbetet följs upp kvartalsvis med rapportering till styrelsen. '
                       'Riskanalys uppdateras årligen eller vid väsentliga förändringar. '
                       'Åtgärder spåras i riskregister med ansvariga och deadlines.')

        self.story.append(Paragraph(plan, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.5*cm))

    def build(self):
        """Generera PDF-filen med header/footer"""
        self.doc.build(self.story, onFirstPage=self._header_footer,
                      onLaterPages=self._header_footer)
        return self.filepath


def create_neab_report(filepath, data):
    """
    Bekvämlighets-funktion för att skapa komplett NEAB-rapport

    Args:
        filepath: Sökväg till output PDF
        data: Dictionary med rapportdata

    Returns:
        Path till genererad PDF
    """
    pdf = NEABPDFTemplate(filepath)

    # Bygg rapport
    pdf.add_cover_page(data)
    pdf.add_executive_summary(data)
    pdf.add_organization_section(data)
    pdf.add_regulatory_summary(data)
    pdf.add_risk_summary(data)
    pdf.add_mitigation_summary(data)
    pdf.add_follow_up_plan(data)

    return pdf.build()