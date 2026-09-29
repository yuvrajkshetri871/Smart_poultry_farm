from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import inch


def generate_farm_report(
    output_path,
    latest,
    analysis,
    ml_risk,
    history
):

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10
    )

    normal_style = styles["BodyText"]

    story = []

    # =====================================================
    # TITLE
    # =====================================================

    story.append(
        Paragraph(
            "SMART POULTRY FARM",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Automatic Farm Analysis Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "This report was automatically generated from "
            "the farm data stored in the Smart Poultry Farm system.",
            normal_style
        )
    )

    story.append(Spacer(1, 15))

    # =====================================================
    # FARM SUMMARY
    # =====================================================

    story.append(
        Paragraph(
            "1. Farm Summary",
            heading_style
        )
    )

    summary_data = [
        ["Parameter", "Value"],
        ["Total Birds", str(latest["birds"])],
        ["Egg Production", str(latest["eggs"]) + " eggs/day"],
        ["Feed Usage", str(latest["feed"]) + " kg"],
        ["Water Usage", str(latest["water"]) + " L"],
        ["Temperature", str(latest["temperature"]) + " °C"],
        ["Humidity", str(latest["humidity"]) + " %"],
        ["Mortality", str(latest["mortality"]) + " birds"],
        ["Performance", str(latest["performance"]) + " %"],
        ["Recorded At", str(latest["created_at"])]
    ]

    table = Table(
        summary_data,
        colWidths=[2.5 * inch, 3.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(table)

    # =====================================================
    # FARM ANALYSIS
    # =====================================================

    story.append(
        Paragraph(
            "2. Farm Analysis",
            heading_style
        )
    )

    analysis_data = [
        ["Analysis", "Result"],
        [
            "Egg Production Rate",
            str(analysis["egg_rate"]) + " %"
        ],
        [
            "Mortality Rate",
            str(analysis["mortality_rate"]) + " %"
        ],
        [
            "Feed Efficiency",
            str(analysis["feed_efficiency"]) + " eggs/kg"
        ],
        [
            "Environmental Risk",
            str(analysis["environmental_risk"])
        ],
        [
            "Overall Farm Risk",
            str(analysis["overall_risk"])
        ],
        [
            "ML Risk Prediction",
            str(ml_risk)
        ]
    ]

    analysis_table = Table(
        analysis_data,
        colWidths=[2.8 * inch, 3.2 * inch]
    )

    analysis_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(analysis_table)

    # =====================================================
    # AUTOMATIC OBSERVATIONS
    # =====================================================

    story.append(
        Paragraph(
            "3. Automatic Observations",
            heading_style
        )
    )

    observations = []

    if analysis["egg_rate"] >= 80:
        observations.append(
            "Egg production rate is currently at or above 80%."
        )
    else:
        observations.append(
            "Egg production rate is below 80%."
        )

    if analysis["mortality_rate"] > 5:
        observations.append(
            "Mortality rate is above 5% and should be monitored."
        )
    else:
        observations.append(
            "Mortality rate is currently at or below 5%."
        )

    observations.append(
        "Environmental risk reported by the farm analysis system: "
        + str(analysis["environmental_risk"])
        + "."
    )

    observations.append(
        "Overall farm risk reported by the farm analysis system: "
        + str(analysis["overall_risk"])
        + "."
    )

    observations.append(
        "Machine learning risk prediction: "
        + str(ml_risk)
        + "."
    )

    for observation in observations:

        story.append(
            Paragraph(
                "• " + observation,
                normal_style
            )
        )

        story.append(Spacer(1, 5))

    # =====================================================
    # FARM HISTORY
    # =====================================================

    story.append(
        Paragraph(
            "4. Farm History",
            heading_style
        )
    )

    history_data = [
        [
            "ID",
            "Birds",
            "Eggs",
            "Feed",
            "Mortality",
            "Performance"
        ]
    ]

    for record in history:

        history_data.append([
            str(record["id"]),
            str(record["birds"]),
            str(record["eggs"]),
            str(record["feed"]),
            str(record["mortality"]),
            str(record["performance"]) + "%"
        ])

    history_table = Table(
        history_data,
        repeatRows=1,
        colWidths=[
            0.45 * inch,
            0.75 * inch,
            0.65 * inch,
            0.75 * inch,
            0.75 * inch,
            1.0 * inch
        ]
    )

    history_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("PADDING", (0, 0), (-1, -1), 4)
        ])
    )

    story.append(history_table)

    # =====================================================
    # FOOTER
    # =====================================================

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated automatically by Smart Poultry Farm.",
            normal_style
        )
    )

    document.build(story)