import csv
import io
from datetime import datetime, date
from flask import current_app, render_template_string
from sqlalchemy import func
from app.models import db, Document, Department, Routing, Categorisation


def daily_inward_register(report_date):
    """Report 1: All documents received on a given date."""
    if isinstance(report_date, str):
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    
    docs = Document.query.filter(
        Document.date_received == report_date
    ).order_by(Document.time_received.asc()).all()
    
    rows = []
    for doc in docs:
        rows.append({
            'tracking_id': doc.tracking_id,
            'date_received': doc.date_received.strftime('%Y-%m-%d'),
            'time_received': doc.time_received.strftime('%H:%M'),
            'mode_of_receipt': doc.mode_of_receipt.replace('_', ' ').title(),
            'sender_name': doc.sender_name,
            'sender_organisation': doc.sender_organisation or '-',
            'subject': doc.subject_description,
            'pages': doc.number_of_pages,
            'status': doc.status,
        })
    
    return {
        'title': f'Daily Inward Register - {report_date.strftime("%d %b %Y")}',
        'headers': ['Tracking ID', 'Date', 'Time', 'Mode', 'Sender', 'Organisation', 'Subject', 'Pages', 'Status'],
        'rows': rows,
        'keys': ['tracking_id', 'date_received', 'time_received', 'mode_of_receipt', 'sender_name', 'sender_organisation', 'subject', 'pages', 'status']
    }


def pending_acknowledgements():
    """Report 2: All documents with status='notified', sorted by SLA deadline."""
    docs = db.session.query(Document, Routing).join(
        Routing, Document.document_id == Routing.document_id
    ).filter(
        Document.status == 'notified'
    ).order_by(Routing.sla_deadline.asc()).all()
    
    rows = []
    for doc, routing in docs:
        rows.append({
            'tracking_id': doc.tracking_id,
            'date_received': doc.date_received.strftime('%Y-%m-%d'),
            'subject': doc.subject_description,
            'department': routing.routed_department.department_name if routing.routed_department else '-',
            'assigned_to': routing.routed_user.full_name if routing.routed_user else '-',
            'sla_deadline': routing.sla_deadline.strftime('%Y-%m-%d %H:%M'),
            'status': doc.status,
        })
    
    return {
        'title': 'Pending Acknowledgements',
        'headers': ['Tracking ID', 'Date Received', 'Subject', 'Department', 'Assigned To', 'SLA Deadline', 'Status'],
        'rows': rows,
        'keys': ['tracking_id', 'date_received', 'subject', 'department', 'assigned_to', 'sla_deadline', 'status']
    }


def overdue_documents():
    """Report 3: All documents with status='escalated'."""
    docs = db.session.query(Document, Routing).join(
        Routing, Document.document_id == Routing.document_id
    ).filter(
        Document.status == 'escalated'
    ).order_by(Routing.sla_deadline.asc()).all()
    
    rows = []
    for doc, routing in docs:
        rows.append({
            'tracking_id': doc.tracking_id,
            'date_received': doc.date_received.strftime('%Y-%m-%d'),
            'subject': doc.subject_description,
            'department': routing.routed_department.department_name if routing.routed_department else '-',
            'assigned_to': routing.routed_user.full_name if routing.routed_user else '-',
            'sla_deadline': routing.sla_deadline.strftime('%Y-%m-%d %H:%M'),
            'overdue_hours': max(0, int((datetime.utcnow() - routing.sla_deadline).total_seconds() / 3600)),
            'status': doc.status,
        })
    
    return {
        'title': 'Overdue Documents',
        'headers': ['Tracking ID', 'Date Received', 'Subject', 'Department', 'Assigned To', 'SLA Deadline', 'Overdue (hrs)', 'Status'],
        'rows': rows,
        'keys': ['tracking_id', 'date_received', 'subject', 'department', 'assigned_to', 'sla_deadline', 'overdue_hours', 'status']
    }


def department_volume(date_from, date_to):
    """Report 4: Count of documents per department for date range."""
    if isinstance(date_from, str):
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    if isinstance(date_to, str):
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    results = db.session.query(
        Department.department_name,
        Department.department_code,
        func.count(Document.document_id).label('count')
    ).join(
        Routing, Department.department_id == Routing.routed_to_department_id
    ).join(
        Document, Routing.document_id == Document.document_id
    ).filter(
        Document.date_received >= date_from,
        Document.date_received <= date_to
    ).group_by(
        Department.department_id
    ).order_by(
        func.count(Document.document_id).desc()
    ).all()
    
    rows = []
    for dept_name, dept_code, count in results:
        rows.append({
            'department_name': dept_name,
            'department_code': dept_code,
            'document_count': count,
        })
    
    return {
        'title': f'Department-wise Volume ({date_from.strftime("%d %b %Y")} to {date_to.strftime("%d %b %Y")})',
        'headers': ['Department', 'Code', 'Document Count'],
        'rows': rows,
        'keys': ['department_name', 'department_code', 'document_count']
    }


def document_type_distribution(date_from, date_to):
    """Report 5: Count by document_type for date range."""
    if isinstance(date_from, str):
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    if isinstance(date_to, str):
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    results = db.session.query(
        Categorisation.document_type,
        func.count(Categorisation.categorisation_id).label('count')
    ).join(
        Document, Categorisation.document_id == Document.document_id
    ).filter(
        Document.date_received >= date_from,
        Document.date_received <= date_to
    ).group_by(
        Categorisation.document_type
    ).order_by(
        func.count(Categorisation.categorisation_id).desc()
    ).all()
    
    rows = []
    for doc_type, count in results:
        rows.append({
            'document_type': doc_type.replace('_', ' ').title(),
            'document_count': count,
        })
    
    return {
        'title': f'Document Type Distribution ({date_from.strftime("%d %b %Y")} to {date_to.strftime("%d %b %Y")})',
        'headers': ['Document Type', 'Count'],
        'rows': rows,
        'keys': ['document_type', 'document_count']
    }


def generate_csv(report_data):
    """Generate CSV string from report data."""
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(report_data['headers'])
    for row in report_data['rows']:
        writer.writerow([row[k] for k in report_data['keys']])
    return si.getvalue()


def generate_pdf(report_data):
    """Generate PDF bytes from report data using WeasyPrint."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }
            h1 { color: #333; font-size: 18px; border-bottom: 2px solid #333; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th { background-color: #2c3e50; color: white; padding: 8px; text-align: left; font-size: 11px; }
            td { padding: 6px 8px; border-bottom: 1px solid #ddd; font-size: 11px; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .footer { margin-top: 20px; font-size: 10px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        <p>Generated on: {{ generated_at }}</p>
        <table>
            <thead>
                <tr>
                {% for header in headers %}
                    <th>{{ header }}</th>
                {% endfor %}
                </tr>
            </thead>
            <tbody>
            {% for row in rows %}
                <tr>
                {% for key in keys %}
                    <td>{{ row[key] }}</td>
                {% endfor %}
                </tr>
            {% endfor %}
            </tbody>
        </table>
        <div class="footer">
            DocTrack — AI-Assisted Document Tracking System | Total Records: {{ rows|length }}
        </div>
    </body>
    </html>
    """
    
    from jinja2 import Template
    template = Template(html_template)
    html = template.render(
        title=report_data['title'],
        headers=report_data['headers'],
        rows=report_data['rows'],
        keys=report_data['keys'],
        generated_at=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    )
    
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
    except Exception as e:
        current_app.logger.error(f'PDF generation failed: {e}')
        return None
