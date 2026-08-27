import csv
import io
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from app.db import db_manager
from app.api.deps import RoleChecker

logger = logging.getLogger(__name__)

router = APIRouter()

allow_researcher_only = RoleChecker(["researcher", "admin"])

@router.get("/export", dependencies=[Depends(allow_researcher_only)])
async def export_report(location: str = "Mangalore-Coast", days: int = 30, format: str = Query("csv", description="Format of the report: csv or pdf")):
    """
    Exports aggregated historical trends and hazard advisories for a given location.
    Accessible only to users with 'researcher' or 'admin' roles.
    """
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    db = db_manager.db
    
    try:
        # 1. Fetch historical readings
        hist_cursor = db["historical_readings"].find({"location": location}).sort("timestamp", -1).limit(days * 4)
        readings = await hist_cursor.to_list(length=None)
        
        # 2. Fetch hazard advisories
        adv_cursor = db["hazard_advisories"].find({"location": location}).sort("created_at", -1).limit(50)
        advisories = await adv_cursor.to_list(length=None)
    except Exception as e:
        logger.error(f"Failed to fetch report data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch report data")
        
    if format.lower() == "pdf":
        return generate_pdf_report(location, advisories, readings)
        
    # Default to CSV format
    return generate_csv_report(location, advisories, readings)


def generate_csv_report(location, advisories, readings):
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([f"ORCA Marine Report for {location}"])
    writer.writerow([f"Generated on: {datetime.utcnow().isoformat()}Z"])
    writer.writerow([])
    
    writer.writerow(["--- HAZARD ADVISORIES ---"])
    writer.writerow(["Date", "Hazard", "Severity", "Action"])
    for adv in advisories:
        writer.writerow([
            adv.get("time", ""),
            adv.get("hazard", ""),
            adv.get("severity", ""),
            adv.get("recommended_action", "")
        ])
        
    writer.writerow([])
    writer.writerow(["--- HISTORICAL READINGS ---"])
    writer.writerow(["Date", "Type", "Value"])
    for reading in readings:
        writer.writerow([
            reading.get("timestamp", ""),
            reading.get("type", ""),
            reading.get("value", "")
        ])
        
    output.seek(0)
    
    filename = f"orca_report_{location.replace(' ', '_').lower()}.csv"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}"
    }
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers=headers)


def generate_pdf_report(location, advisories, readings):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Normal']
    
    # Title
    elements.append(Paragraph(f"ORCA Marine Report: {location}", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.utcnow().isoformat()}Z", subtitle_style))
    elements.append(Spacer(1, 20))
    
    # Advisories Table
    elements.append(Paragraph("Hazard Advisories", styles['Heading2']))
    adv_data = [["Date", "Hazard", "Severity", "Action"]]
    for adv in advisories:
        adv_data.append([
            str(adv.get("time", ""))[:10],
            str(adv.get("hazard", "")),
            str(adv.get("severity", "")),
            str(adv.get("recommended_action", ""))[:50]
        ])
        
    if len(adv_data) > 1:
        adv_table = Table(adv_data)
        adv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(adv_table)
    else:
        elements.append(Paragraph("No advisories found for this period.", styles['Normal']))
        
    elements.append(Spacer(1, 20))
    
    # Readings Table
    elements.append(Paragraph("Historical Readings (Sample)", styles['Heading2']))
    read_data = [["Date", "Type", "Value"]]
    for reading in readings[:50]: # Limit to 50 for PDF brevity
        read_data.append([
            str(reading.get("timestamp", ""))[:10],
            str(reading.get("type", "")),
            str(reading.get("value", ""))
        ])
        
    if len(read_data) > 1:
        read_table = Table(read_data)
        read_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.aliceblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(read_table)
    else:
        elements.append(Paragraph("No readings found for this period.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    
    filename = f"orca_report_{location.replace(' ', '_').lower()}.pdf"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}"
    }
    return StreamingResponse(iter([buffer.getvalue()]), media_type="application/pdf", headers=headers)
