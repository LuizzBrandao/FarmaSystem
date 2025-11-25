from io import BytesIO
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.colors import HexColor


class PDFReportGenerator:
    """Gerador de relatórios em PDF para o sistema de farmácia"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.primary_color = HexColor('#2563eb')
        self.secondary_color = HexColor('#10b981')
        self.danger_color = HexColor('#ef4444')
        self.warning_color = HexColor('#f59e0b')
        
    def create_header_style(self):
        """Criar estilo para cabeçalho"""
        return ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=self.primary_color,
            alignment=1  # Centro
        )
    
    def create_subheader_style(self):
        """Criar estilo para subcabeçalho"""
        return ParagraphStyle(
            'CustomSubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=self.primary_color
        )
    
    def add_header(self, story, title, subtitle=None):
        """Adicionar cabeçalho ao relatório"""
        header_style = self.create_header_style()
        story.append(Paragraph(title, header_style))
        
        if subtitle:
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.grey,
                alignment=1,
                spaceAfter=20
            )
            story.append(Paragraph(subtitle, subtitle_style))
        
        story.append(Spacer(1, 12))
    
    def add_info_section(self, story, data):
        """Adicionar seção de informações gerais"""
        info_data = [
            ['Data de Geração:', timezone.localtime().strftime('%d/%m/%Y %H:%M:%S')],
            ['Sistema:', 'FarmaSystem - Gestão de Farmácia'],
        ]
        
        for key, value in data.items():
            info_data.append([f"{key}:", str(value)])
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
    
    def generate_stock_report(self, medications):
        """Gerar relatório de estoque"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Cabeçalho
        self.add_header(
            story, 
            "Relatório de Estoque de Medicamentos",
            f"Total de medicamentos: {len(medications)}"
        )
        
        # Informações gerais
        total_stock = sum(med.current_stock for med in medications)
        low_stock_count = sum(1 for med in medications if med.is_low_stock)
        
        self.add_info_section(story, {
            'Total de Medicamentos': len(medications),
            'Estoque Total': f"{total_stock} unidades",
            'Medicamentos com Estoque Baixo': low_stock_count
        })
        
        # Tabela de medicamentos
        subheader_style = self.create_subheader_style()
        story.append(Paragraph("Detalhes do Estoque", subheader_style))
        
        data = [['Medicamento', 'Categoria', 'Estoque Atual', 'Estoque Mínimo', 'Status']]
        
        for med in medications:
            status = "⚠️ Baixo" if med.is_low_stock else "✅ OK"
            data.append([
                med.name,
                med.category.name,
                str(med.current_stock),
                str(med.minimum_stock),
                status
            ])
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(table)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_expiry_report(self, stock_items):
        """Gerar relatório de vencimentos"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Cabeçalho
        self.add_header(
            story,
            "Relatório de Vencimentos",
            f"Total de lotes: {len(stock_items)}"
        )
        
        # Separar por status
        expired = [item for item in stock_items if item.is_expired]
        near_expiry = [item for item in stock_items if item.is_near_expiry and not item.is_expired]
        
        self.add_info_section(story, {
            'Total de Lotes': len(stock_items),
            'Lotes Vencidos': len(expired),
            'Próximos ao Vencimento': len(near_expiry)
        })
        
        # Medicamentos vencidos
        if expired:
            subheader_style = self.create_subheader_style()
            story.append(Paragraph("🚨 Medicamentos Vencidos", subheader_style))
            
            data = [['Medicamento', 'Quantidade', 'Data de Vencimento']]
            for item in expired:
                data.append([
                    item.medication.name,
                    str(item.quantity),
                    item.expiry_date.strftime('%d/%m/%Y')
                ])
            
            table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.danger_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Próximos ao vencimento
        if near_expiry:
            story.append(Paragraph("⚠️ Próximos ao Vencimento (30 dias)", subheader_style))
            
            data = [['Medicamento', 'Quantidade', 'Data de Vencimento']]
            for item in near_expiry:
                data.append([
                    item.medication.name,
                    str(item.quantity),
                    item.expiry_date.strftime('%d/%m/%Y')
                ])
            
            table = Table(data, colWidths=[3*inch, 1*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.warning_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            story.append(table)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_movement_report(self, movements):
        """Gerar relatório de movimentações"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Cabeçalho
        self.add_header(
            story,
            "Relatório de Movimentações",
            f"Total de movimentações: {len(movements)}"
        )
        
        # Resumo por tipo
        entrada_count = len([m for m in movements if m.movement_type == 'entrada'])
        saida_count = len([m for m in movements if m.movement_type == 'saida'])
        
        self.add_info_section(story, {
            'Total de Movimentações': len(movements),
            'Entradas': entrada_count,
            'Saídas': saida_count
        })
        
        # Tabela de movimentações
        subheader_style = self.create_subheader_style()
        story.append(Paragraph("Histórico de Movimentações", subheader_style))
        
        data = [['Data', 'Medicamento', 'Tipo', 'Quantidade', 'Usuário']]
        
        for movement in movements:
            movement_type = movement.get_movement_type_display()
            quantity_str = f"+{movement.quantity}" if movement.movement_type == 'entrada' else f"-{movement.quantity}"
            
            data.append([
                movement.created_at.strftime('%d/%m/%Y'),
                movement.medication.name,
                movement_type,
                quantity_str,
                movement.user.get_full_name() or movement.user.username
            ])
        
        table = Table(data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(table)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
