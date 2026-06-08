import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "sample_financial_data.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

DASHBOARD_PATH = OUTPUT_DIR / "financial_dashboard.png"
PDF_PATH = OUTPUT_DIR / "automated_financial_report.pdf"
EXCEL_PATH = OUTPUT_DIR / "financial_summary.xlsx"


def currency(x):
    return f"${x:,.0f}"


def percent(x):
    return f"{x:.1f}%"


def money_formatter(x, pos):
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.1f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.0f}K"
    return f"${x:.0f}"


def load_financial_data(path):
    df = pd.read_csv(path)

    df["Month_Label"] = pd.to_datetime(df["Month"]).dt.strftime("%b")

    df["Net_Profit"] = df["Revenue"] - (
        df["COGS"]
        + df["Operating_Expenses"]
        + df["Marketing_Spend"]
    )

    df["Net_Margin"] = (
        df["Net_Profit"] / df["Revenue"] * 100
    )

    return df


def calculate_metrics(df):
    metrics = {
        "total_revenue": df["Revenue"].sum(),
        "total_expenses": (
            df["COGS"].sum()
            + df["Operating_Expenses"].sum()
            + df["Marketing_Spend"].sum()
        ),
        "total_net_profit": df["Net_Profit"].sum(),
        "avg_net_margin": df["Net_Margin"].mean(),
        "best_month": df.loc[df["Net_Profit"].idxmax(), "Month_Label"],
        "worst_month": df.loc[df["Net_Profit"].idxmin(), "Month_Label"],
    }

    return metrics


def create_dashboard(df, metrics):
    plt.rcParams["font.family"] = "DejaVu Sans"

    fig = plt.figure(figsize=(19, 11), facecolor="#0F172A")

    fig.suptitle(
        "Automated Financial Reporting Dashboard",
        fontsize=24,
        fontweight="bold",
        color="#FFFFFF",
        y=0.96,
    )

    card_positions = [
        (0.05, 0.75, 0.20, 0.12),
        (0.28, 0.75, 0.20, 0.12),
        (0.51, 0.75, 0.20, 0.12),
        (0.74, 0.75, 0.20, 0.12),
    ]

    kpis = [
        ("Total Revenue", currency(metrics["total_revenue"]), "#38BDF8"),
        ("Net Profit", currency(metrics["total_net_profit"]), "#4ADE80"),
        ("Avg. Net Margin", percent(metrics["avg_net_margin"]), "#DDD6FE"),
        ("Best Month", metrics["best_month"], "#FACC15"),
    ]

    for pos, (label, value, accent) in zip(card_positions, kpis):
        ax = fig.add_axes(pos)

        ax.set_facecolor("#111827")

        for spine in ax.spines.values():
            spine.set_edgecolor(accent)
            spine.set_linewidth(1.8)

        ax.set_xticks([])
        ax.set_yticks([])

        ax.text(
            0.05,
            0.65,
            label,
            color="#E5E7EB",
            fontsize=11,
            transform=ax.transAxes,
        )

        ax.text(
            0.05,
            0.22,
            value,
            color="#FFFFFF",
            fontsize=22,
            fontweight="bold",
            transform=ax.transAxes,
        )

    ax1 = fig.add_axes((0.05, 0.40, 0.50, 0.28), facecolor="#111827")

    ax1.plot(
        df["Month_Label"],
        df["Revenue"],
        marker="o",
        linewidth=3,
        label="Revenue",
        color="#38BDF8",
    )

    ax1.plot(
        df["Month_Label"],
        df["Net_Profit"],
        marker="o",
        linewidth=3,
        label="Net Profit",
        color="#4ADE80",
    )

    ax1.set_title(
        "Revenue vs Net Profit",
        color="#FFFFFF",
        fontsize=18,
        fontweight="bold",
    )

    ax1.tick_params(colors="#CBD5E1", labelsize=11)
    ax1.yaxis.set_major_formatter(FuncFormatter(money_formatter))
    ax1.grid(True, alpha=0.15)

    ax1.legend(
        facecolor="#111827",
        edgecolor="#334155",
        labelcolor="#FFFFFF",
        fontsize=10,
    )

    for spine in ax1.spines.values():
        spine.set_color("#334155")

    ax2 = fig.add_axes((0.70, 0.44, 0.22, 0.22), facecolor="#111827")

    expense_totals = [
        df["COGS"].sum(),
        df["Operating_Expenses"].sum(),
        df["Marketing_Spend"].sum(),
    ]

    labels = ["COGS", "Operations", "Marketing"]

    colors_list = ["#F97316", "#A78BFA", "#22D3EE"]

    ax2.pie(
        expense_totals,
        labels=labels,
        autopct="%1.1f%%",
        startangle=120,
        colors=colors_list,
        textprops={"color": "#FFFFFF", "fontsize": 9},
    )

    ax2.set_title(
        "Expense Breakdown",
        color="#FFFFFF",
        fontsize=16,
        fontweight="bold",
    )

    ax3 = fig.add_axes((0.05, 0.08, 0.60, 0.23), facecolor="#111827")

    ax3.bar(
        df["Month_Label"],
        df["Net_Margin"],
        color="#E9D5FF",
        edgecolor="#F5D0FE",
    )

    avg_margin = metrics["avg_net_margin"]



    ax3.set_title(
        "Monthly Net Margin %",
        color="#FFFFFF",
        fontsize=18,
        fontweight="bold",
    )

    ax3.tick_params(colors="#CBD5E1", labelsize=11)
    ax3.grid(True, axis="y", alpha=0.12)



    for spine in ax3.spines.values():
        spine.set_color("#334155")

    ax4 = fig.add_axes((0.66, 0.05, 0.30, 0.18))

    ax4.set_facecolor("#111827")

    for spine in ax4.spines.values():
        spine.set_edgecolor("#475569")
        spine.set_linewidth(1.2)

    ax4.set_xticks([])
    ax4.set_yticks([])

    insight_text = (
        f"• Revenue reached {currency(metrics['total_revenue'])}\n\n"
        f"• Net profit closed at {currency(metrics['total_net_profit'])}\n\n"
        f"• Avg margin was {percent(metrics['avg_net_margin'])}\n\n"
        f"• Best month: {metrics['best_month']}\n\n"
        f"• Risk month: {metrics['worst_month']}"
    )

    ax4.text(
        0.04,
        0.92,
        "Automated Insights",
        fontsize=16,
        fontweight="bold",
        color="#FFFFFF",
        va="top",
    )

    ax4.text(
        0.04,
        0.74,
        insight_text,
        fontsize=10,
        color="#E2E8F0",
        va="top",
    )

    plt.savefig(
        DASHBOARD_PATH,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close()


def create_pdf_report(df: pd.DataFrame, metrics: dict):
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=landscape(A4),
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch,
    
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=26,
        leading=30,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=18,
    )

    title_style.alignment=1

    story = []

    story.append(
        Paragraph("Automated Financial Report", title_style)
    )

    kpi_table_data = [
        ["Revenue", "Total Expenses", "Net Profit", "Avg. Net Margin", "Best Month"],
        [
            currency(metrics["total_revenue"]),
            currency(metrics["total_expenses"]),
            currency(metrics["total_net_profit"]),
            percent(metrics["avg_net_margin"]),
            metrics["best_month"],
        ],
    ]

    kpi_table = Table(kpi_table_data, colWidths=[1.5 * inch] * 5)

    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
            ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#0F172A")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 9),
        ])
    )

    story.append(kpi_table)

    story.append(Spacer(1, 0.08 * inch))

    dashboard_img = Image(
        str(DASHBOARD_PATH),
        width=10.2 * inch,
        height=5.5 * inch,
    )

    story.append(dashboard_img)

    doc.build(story)


def export_excel_summary(df):
    summary = df[
        [
            "Month_Label",
            "Revenue",
            "COGS",
            "Operating_Expenses",
            "Marketing_Spend",
            "Net_Profit",
            "Net_Margin",
        ]
    ]

    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Financial Summary")


def main():
    df = load_financial_data(DATA_PATH)

    metrics = calculate_metrics(df)

    create_dashboard(df, metrics)

    create_pdf_report(df,metrics)

    export_excel_summary(df)

    print("Automated Financial Reporting System completed.")
    print(f"Dashboard saved to: {DASHBOARD_PATH}")
    print(f"PDF report saved to: {PDF_PATH}")
    print(f"Excel summary saved to: {EXCEL_PATH}")


if __name__ == "__main__":
    main()