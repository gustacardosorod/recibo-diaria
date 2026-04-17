from flask import Flask, render_template, request, send_file, make_response
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import io
import os
from datetime import datetime
from random import randint

app = Flask(__name__)
COUNTER_FILE = "contador_recibo.txt"

def gerar_numero_sequencial():
    try:
        if not os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "w") as f:
                f.write("1")
            return "00001"

        with open(COUNTER_FILE, "r") as f:
            conteudo = f.read().strip()

        numero = int(conteudo) if conteudo else 1

        with open(COUNTER_FILE, "w") as f:
            f.write(str(numero + 1))

        return str(numero).zfill(5)
    except Exception as e:
        print(f"Erro: {e}")
        return str(randint(10000, 99999))

CNPJS = [
    {"label": "Viação Águia Branca S/A – Matriz", "value": "33.216.104/0001-00"},
    {"label": "Viação Águia Branca S/A – Filial 1", "value": "33.216.104/0002-81"},
    {"label": "Viação Águia Branca S/A – Filial 2", "value": "33.216.104/0003-62"},
]

TIPOS_ADICIONAL = [
    "Alimentação",
    "Hotelaria",
    "Pedágio",
    "Estacionamento",
    "Combustível",
    "Manutenção",
    "Outros",
]

@app.route("/")
def index():
    return render_template("index.html", cnpjs=CNPJS, tipos=TIPOS_ADICIONAL)

@app.route("/gerar-pdf", methods=["POST"])
def gerar_pdf():
    try:
        data = request.json or {}
        numero = gerar_numero_sequencial()
        data["numero"] = numero

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()
        elems = []

        AZUL = colors.HexColor("#003087")
        AMARELO = colors.HexColor("#FFB800")
        CINZA_CLARO = colors.HexColor("#f4f6fa")
        CINZA_ESCURO = colors.HexColor("#6b7a99")
        BRANCO = colors.white
        PRETO = colors.black

        W = A4[0] - 30 * mm

        def brl(v):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        def fmt_data(d):
            if not d:
                return "—"
            partes = d.split("-")
            if len(partes) == 3:
                return f"{partes[2]}/{partes[1]}/{partes[0]}"
            return d

        header_style = ParagraphStyle(
            "header",
            parent=styles["Normal"],
            fontSize=16,
            leading=18,
            textColor=BRANCO,
            fontName="Helvetica-Bold",
            alignment=TA_LEFT
        )

        numero_style = ParagraphStyle(
            "numero",
            parent=styles["Normal"],
            fontSize=11,
            leading=11,
            textColor=BRANCO,
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT
        )

        header_data = [[
            Paragraph("VIAÇÃO ÁGUIA BRANCA", header_style),
            Paragraph(f"Recibo Nº&nbsp;<b>{numero}</b>", numero_style)
        ]]
        header = Table(header_data, colWidths=[W - 95, 95])
        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), AZUL),
            ("TEXTCOLOR", (0, 0), (-1, -1), BRANCO),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 15),
            ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ]))

        elems.append(header)
        elems.append(Spacer(1, 15))

        titulo_secao = ParagraphStyle(
            "titulo_secao",
            parent=styles["Normal"],
            fontSize=10,
            textColor=AZUL,
            fontName="Helvetica-Bold",
            alignment=TA_LEFT,
            spaceAfter=6,
            spaceBefore=8
        )

        PAD_TAG = 0
        PAD_VAL = 0
        ALTURA = 2

        elems.append(Paragraph("DADOS DA EMPRESA", titulo_secao))
        empresa_data = [
            ["Empresa:", data.get("empresa", "Viação Águia Branca S/A")],
            ["CNPJ:", data.get("cnpj", "—")]
        ]
        empresa_table = Table(empresa_data, colWidths=[28 * mm, W - 28 * mm])
        empresa_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), CINZA_ESCURO),
            ("TEXTCOLOR", (1, 0), (1, -1), PRETO),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), ALTURA),
            ("TOPPADDING", (0, 0), (-1, -1), ALTURA),
            ("LEFTPADDING", (0, 0), (0, -1), PAD_TAG),
            ("RIGHTPADDING", (0, 0), (0, -1), 3),
            ("LEFTPADDING", (1, 0), (1, -1), PAD_VAL),
            ("RIGHTPADDING", (1, 0), (1, -1), PAD_VAL),
        ]))
        elems.append(empresa_table)
        elems.append(Spacer(1, 2))

        elems.append(Paragraph("DADOS DO MOTORISTA", titulo_secao))
        motorista_data = [
            ["Matrícula:", data.get("matricula", "—")],
            ["Motorista:", data.get("nome", "—")]
        ]
        motorista_table = Table(motorista_data, colWidths=[28 * mm, W - 28 * mm])
        motorista_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), CINZA_ESCURO),
            ("TEXTCOLOR", (1, 0), (1, -1), PRETO),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), ALTURA),
            ("TOPPADDING", (0, 0), (-1, -1), ALTURA),
            ("LEFTPADDING", (0, 0), (0, -1), PAD_TAG),
            ("RIGHTPADDING", (0, 0), (0, -1), 3),
            ("LEFTPADDING", (1, 0), (1, -1), PAD_VAL),
            ("RIGHTPADDING", (1, 0), (1, -1), PAD_VAL),
        ]))
        elems.append(motorista_table)
        elems.append(Spacer(1, 3))

        elems.append(Paragraph("DADOS DA VIAGEM", titulo_secao))

        codigo_servico = data.get("codigo_servico", "")
        destino = data.get("destino", "—")
        partida = f"{fmt_data(data.get('data_partida', ''))} {data.get('hora_partida', '')}".strip()
        chegada = f"{fmt_data(data.get('data_chegada', ''))} {data.get('hora_chegada', '')}".strip()

        viagem_data = []
        if codigo_servico:
            viagem_data.append(["Cód. Serviço:", codigo_servico, "", ""])
        viagem_data.append(["Destino:", destino, "", ""])
        viagem_data.append(["Partida:", partida or "—", "Chegada:", chegada or "—"])

        viagem_table = Table(
            viagem_data,
            colWidths=[30 * mm, 58 * mm, 30 * mm, W - (30 * mm + 58 * mm + 30 * mm)]
        )
        viagem_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), CINZA_ESCURO),
            ("TEXTCOLOR", (1, 0), (1, -1), PRETO),
            ("TEXTCOLOR", (2, 0), (2, -1), CINZA_ESCURO),
            ("TEXTCOLOR", (3, 0), (3, -1), PRETO),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), ALTURA),
            ("TOPPADDING", (0, 0), (-1, -1), ALTURA),
            ("LEFTPADDING", (0, 0), (0, -1), PAD_TAG),
            ("RIGHTPADDING", (0, 0), (0, -1), 3),
            ("LEFTPADDING", (1, 0), (1, -1), PAD_VAL),
            ("RIGHTPADDING", (1, 0), (1, -1), PAD_VAL),
            ("LEFTPADDING", (2, 0), (2, -1), 8),
            ("RIGHTPADDING", (2, 0), (2, -1), 3),
            ("LEFTPADDING", (3, 0), (3, -1), PAD_VAL),
            ("RIGHTPADDING", (3, 0), (3, -1), PAD_VAL),
        ]))
        elems.append(viagem_table)
        elems.append(Spacer(1, 3))

        qtd = float(data.get("qtd_diarias", 1))
        val = float(data.get("valor_diaria", 0))
        subtotal = qtd * val
        adicionais = data.get("adicionais", [])
        total_add = sum(float(a.get("valor", 0)) for a in adicionais if a.get("valor"))
        total = subtotal + total_add

        tabela_dados = [["Descrição", "Qtd.", "Unitário", "Total"]]
        tabela_dados.append(["Diária de motorista", str(int(qtd)), brl(val), brl(subtotal)])

        for a in adicionais:
            valor = float(a.get("valor", 0) or 0)
            if a.get("tipo") and valor > 0:
                tabela_dados.append([a.get("tipo"), "—", "—", brl(valor)])

        tabela_dados.append(["TOTAL GERAL", "", "", brl(total)])

        table = Table(tabela_dados, colWidths=[W * 0.45, W * 0.12, W * 0.18, W * 0.25])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZUL),
            ("TEXTCOLOR", (0, 0), (-1, 0), BRANCO),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (1, 0), (3, 0), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -2), 8),
            ("ALIGN", (1, 1), (2, -2), "CENTER"),
            ("ALIGN", (3, 1), (3, -2), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 1), (-1, -2), 5),
            ("TOPPADDING", (0, 1), (-1, -2), 5),
            ("GRID", (0, 0), (-1, -2), 0.3, colors.lightgrey),
            ("BACKGROUND", (0, -1), (-1, -1), AZUL),
            ("TEXTCOLOR", (0, -1), (-1, -1), BRANCO),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -1), (-1, -1), 10),
            ("ALIGN", (0, -1), (-2, -1), "LEFT"),
            ("ALIGN", (-1, -1), (-1, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
            ("TOPPADDING", (0, -1), (-1, -1), 6),
        ]))

        for i in range(1, len(tabela_dados) - 1):
            if i % 2 == 1:
                table.setStyle(TableStyle([("BACKGROUND", (0, i), (-1, i), CINZA_CLARO)]))

        elems.append(table)
        elems.append(Spacer(1, 15))

        declaracao_style = ParagraphStyle(
            "declaracao",
            parent=styles["Normal"],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=PRETO,
            spaceAfter=8
        )
        elems.append(Paragraph(
            f"Recebi o valor total de <b>{brl(total)}</b> referente às diárias e custos adicionais da viagem.",
            declaracao_style
        ))

        elems.append(Spacer(1, 15))

        rodape_style = ParagraphStyle(
            "rodape",
            parent=styles["Normal"],
            fontSize=7,
            alignment=TA_CENTER,
            textColor=CINZA_ESCURO,
            spaceAfter=5
        )
        hoje = datetime.now().strftime("%d/%m/%Y às %H:%M")
        elems.append(Paragraph(
            f"Documento emitido eletronicamente em {hoje} • Recibo Nº {numero} • Sistema Viação Águia Branca",
            rodape_style
        ))

        doc.build(elems)
        buffer.seek(0)

        response = make_response(send_file(
            buffer,
            as_attachment=True,
            download_name=f"recibo_aguia_branca_{numero}.pdf",
            mimetype="application/pdf"
        ))
        response.headers["X-Recibo-Numero"] = numero
        return response

    except Exception as e:
        print(f"Erro: {e}")
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)