#!/usr/bin/env python3
"""
seed_mock_data.py — Comprehensive mock data seeder for DocTrack.

Creates 6 departments, 16 users, 60 documents with full lifecycle records.
Simulates a CISCE Hyderabad Regional Centre office that has been operational
for approximately 3 months.

Usage:
    python seed_mock_data.py
"""

import random
import bcrypt
from datetime import datetime, date, time, timedelta
from app import create_app
from app.models import (
    db, Department, User, Document, Categorisation,
    Routing, Notification, Acknowledgement,
    TrackingEvent, AuditLog,
)

random.seed(42)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(
        password.encode('utf-8'), bcrypt.gensalt(rounds=12)
    ).decode('utf-8')


def rand_time(hour_min=9, hour_max=17):
    h = random.randint(hour_min, hour_max)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return time(h, m, s)


def rand_mode():
    return random.choice([
        'courier', 'speed_post', 'registered_post', 'hand_delivery',
    ])


def dt_offset(days_ago, extra_hours=0, extra_minutes=0):
    """Return a datetime `days_ago` days before now with optional offset."""
    return datetime.utcnow() - timedelta(
        days=days_ago, hours=-extra_hours, minutes=-extra_minutes,
    )


ACK_REMARKS = [
    "Received and noted. Filed for reference.",
    "Document received, will process by EOD.",
    "Acknowledged, forwarding to concerned officer.",
    "Received. Necessary action being initiated.",
    "Noted. Will be taken up in the next review meeting.",
    "Acknowledged. Compliance report will be submitted shortly.",
    "Received with thanks. Under review.",
    "Document received and placed before competent authority.",
    "Acknowledged. Reply is being drafted.",
    "Received. Relevant section informed for necessary action.",
    "Noted. Will coordinate with other departments as required.",
    "Acknowledged. File has been put up for approval.",
    "Received. Action initiated as per directions.",
    "Acknowledged and filed under the concerned subject head.",
    "Document received. No further action required at this stage.",
]

# ---------------------------------------------------------------------------
# Department definitions
# ---------------------------------------------------------------------------

DEPARTMENTS = [
    {'name': 'Finance and Accounts',  'code': 'FINAC'},
    {'name': 'Human Resources',       'code': 'HR'},
    {'name': 'Information Technology', 'code': 'IT'},
    {'name': 'Legal and Compliance',   'code': 'LEGAL'},
    {'name': 'Administration',         'code': 'ADMIN'},
    {'name': 'Audit and Inspection',   'code': 'AUDIT'},
]

# ---------------------------------------------------------------------------
# User definitions
# ---------------------------------------------------------------------------

USERS = [
    # Super Admin
    {'username': 'superadmin', 'password': 'Admin@123',
     'full_name': 'Rajesh Kumar Sharma', 'email': 'superadmin@doctrack.gov.in',
     'role': 'superadmin', 'dept_code': None},
    # Admin
    {'username': 'admin', 'password': 'Admin@123',
     'full_name': 'Priya Venkataraman', 'email': 'admin@doctrack.gov.in',
     'role': 'admin', 'dept_code': None},
    # Receptionists
    {'username': 'reception1', 'password': 'Admin@123',
     'full_name': 'Sunita Devi', 'email': 'sunita@doctrack.gov.in',
     'role': 'receptionist', 'dept_code': None},
    {'username': 'reception2', 'password': 'Admin@123',
     'full_name': 'Mohammed Rafi Khan', 'email': 'rafi@doctrack.gov.in',
     'role': 'receptionist', 'dept_code': None},
    # Finance
    {'username': 'fin_user1', 'password': 'Admin@123',
     'full_name': 'Arvind Mishra', 'email': 'fin_user1@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'FINAC', 'is_head': True},
    {'username': 'fin_user2', 'password': 'Admin@123',
     'full_name': 'Lakshmi Nair', 'email': 'fin_user2@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'FINAC'},
    # HR
    {'username': 'hr_user1', 'password': 'Admin@123',
     'full_name': 'Deepa Krishnan', 'email': 'hr_user1@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'HR', 'is_head': True},
    {'username': 'hr_user2', 'password': 'Admin@123',
     'full_name': 'Sanjay Tiwari', 'email': 'hr_user2@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'HR'},
    # IT
    {'username': 'it_user1', 'password': 'Admin@123',
     'full_name': 'Karthik Subramanian', 'email': 'it_user1@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'IT', 'is_head': True},
    {'username': 'it_user2', 'password': 'Admin@123',
     'full_name': 'Anjali Gupta', 'email': 'it_user2@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'IT'},
    # Legal
    {'username': 'legal_user1', 'password': 'Admin@123',
     'full_name': 'Advocate Ramesh Pandey', 'email': 'legal_user1@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'LEGAL', 'is_head': True},
    {'username': 'legal_user2', 'password': 'Admin@123',
     'full_name': 'Meera Joshi', 'email': 'legal_user2@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'LEGAL'},
    # Admin (department)
    {'username': 'admin_user1', 'password': 'Admin@123',
     'full_name': 'Prakash Rao', 'email': 'admin_user1@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'ADMIN', 'is_head': True},
    {'username': 'admin_user2', 'password': 'Admin@123',
     'full_name': 'Fatima Sheikh', 'email': 'admin_user2@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'ADMIN'},
    # Audit
    {'username': 'audit_user1', 'password': 'Admin@123',
     'full_name': 'Suresh Babu', 'email': 'audit_user1@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'AUDIT', 'is_head': True},
    {'username': 'audit_user2', 'password': 'Admin@123',
     'full_name': 'Nandini Verma', 'email': 'audit_user2@doctrack.gov.in',
     'role': 'dept_user', 'dept_code': 'AUDIT'},
]

# ---------------------------------------------------------------------------
# Document definitions  (60 documents)
# ---------------------------------------------------------------------------
# Each tuple: (days_ago, sender_name, sender_org, subject, dept_code,
#              doc_type, pages, target_status, ocr_text_key)
# ---------------------------------------------------------------------------

DOCS = [
    # ======================================================================
    # GROUP 1 — ACKNOWLEDGED, 60-90 days ago  (10 docs)
    # ======================================================================
    {
        'days': 88, 'sender': 'Shri R.K. Gupta, Under Secretary',
        'org': 'Ministry of Finance, Department of Expenditure, North Block, New Delhi',
        'addr': 'Room No. 245-A, North Block, Central Secretariat, New Delhi-110001',
        'subject': 'Revised Dearness Allowance rates effective from 01.01.2025 for Central Govt employees',
        'dept': 'FINAC', 'doc_type': 'circular', 'pages': 4, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "GOVERNMENT OF INDIA\nMINISTRY OF FINANCE\nDEPARTMENT OF EXPENDITURE\n\nOffice Memorandum No. 1/1/2025-E-II(B)\nDated: New Delhi, the 15th March, 2025\n\nSubject: Revised rates of Dearness Allowance to Central Government employees — Revised Rates effective from 01.01.2025.\n\nThe undersigned is directed to refer to this Ministry's Office Memorandum No. 1/2/2024-E-II(B) dated 12th October, 2024, on the subject mentioned above and to state that the President is pleased to decide that the Dearness Allowance payable to Central Government employees shall be enhanced from the existing rate of 50% to 53% of the basic pay with effect from 1st January, 2025.\n\nThe term 'basic pay' in the revised pay structure means the pay drawn in the prescribed Level in the Pay Matrix as per 7th CPC recommendations. The payment on account of Dearness Allowance involving fractions of 50 paise and above shall be rounded to the next higher rupee and fractions of less than 50 paise shall be ignored.\n\nAll Ministries/Departments are requested to bring the contents of this Office Memorandum to the notice of the Controller of Accounts/Pay and Accounts Officers working under them.\n\n(R.K. Gupta)\nUnder Secretary to the Government of India",
    },
    {
        'days': 85, 'sender': 'Registrar (Judicial), High Court of Telangana',
        'org': 'High Court of Telangana, High Court Building, Hyderabad',
        'addr': 'High Court Buildings, Gachibowli, Hyderabad, Telangana-500032',
        'subject': 'Legal notice in matter of WP No. 4521/2025 regarding service conditions of staff',
        'dept': 'LEGAL', 'doc_type': 'legal_notice', 'pages': 8, 'status': 'acknowledged',
        'mode': 'registered_post',
        'ocr': "IN THE HIGH COURT OF TELANGANA AT HYDERABAD\n\nW.P. No. 4521 of 2025\n\nBetween:\nTelangana State Government Employees Association ... Petitioner\nVersus\nState of Telangana and Others ... Respondents\n\nTO,\nThe Regional Director, CISCE Hyderabad Regional Centre\nHyderabad, Telangana\n\nSir/Madam,\n\nYou are hereby notified that the above Writ Petition has been filed challenging certain conditions of service applicable to contractual staff. The Hon'ble Court has been pleased to issue notice and the matter is posted for hearing on 15.04.2025. You are directed to file a counter-affidavit within four weeks from the date of receipt of this notice.\n\nThe petitioners have challenged the validity of Office Order No. HR/2024/1287 dated 23.11.2024 issued by your office on the grounds that it violates Article 14 and 16 of the Constitution of India.\n\nYou are requested to take immediate steps to engage counsel and file necessary counter before the next date of hearing.\n\n(Sd/-)\nRegistrar (Judicial)\nHigh Court of Telangana",
    },
    {
        'days': 82, 'sender': 'Executive Engineer, CPWD Division-III',
        'org': 'Central Public Works Department (CPWD), Hyderabad Division',
        'addr': 'CPWD Complex, Sultan Bazar, Koti, Hyderabad-500195',
        'subject': 'Tender notice for annual maintenance and renovation of office building — FY 2025-26',
        'dept': 'ADMIN', 'doc_type': 'tender', 'pages': 12, 'status': 'acknowledged',
        'mode': 'courier',
        'ocr': "CENTRAL PUBLIC WORKS DEPARTMENT\nOFFICE OF THE EXECUTIVE ENGINEER, CPWD DIVISION-III, HYDERABAD\n\nNIT No. CPWD/HYD-III/2025-26/AMC/017\nDated: 10.03.2025\n\nTENDER NOTICE\n\nSealed tenders are invited on behalf of the President of India from eligible and experienced contractors for the following work:\n\nName of Work: Annual Maintenance Contract and Interior Renovation of CISCE Regional Centre Office Building, Banjara Hills, Hyderabad.\n\nEstimated Cost: Rs. 18,45,000/- (Rupees Eighteen Lakhs Forty-Five Thousand Only)\nEarnest Money: Rs. 36,900/-\nTime of Completion: 90 days from date of award\nLast Date of Submission: 25.04.2025 at 15:00 Hours\n\nScope of Work includes repair of flooring, painting, electrical rewiring of first floor, plumbing works, false ceiling replacement in conference hall, and HVAC maintenance. Detailed NIT and tender documents may be downloaded from the CPWD e-procurement portal or collected from this office on payment of Rs. 500/- (non-refundable).\n\n(Sd/-)\nExecutive Engineer\nCPWD Division-III, Hyderabad",
    },
    {
        'days': 78, 'sender': 'Shri M. Venkateshwarlu, Director of Audit',
        'org': 'Office of the Comptroller and Auditor General (CAG), Hyderabad',
        'addr': 'A.G. Office Complex, Saifabad, Hyderabad-500004',
        'subject': 'Compliance audit report on utilisation of grants for FY 2023-24',
        'dept': 'AUDIT', 'doc_type': 'audit', 'pages': 15, 'status': 'acknowledged',
        'mode': 'hand_delivery',
        'ocr': "COMPTROLLER AND AUDITOR GENERAL OF INDIA\nOFFICE OF THE PRINCIPAL DIRECTOR OF AUDIT (CENTRAL), HYDERABAD\n\nAudit Report No. PDA/HYD/C-17/2025\nDated: 20.03.2025\n\nSubject: Compliance Audit Report on Utilisation of Grants received from MHRD for the Financial Year 2023-24.\n\nDear Sir/Madam,\n\nThis office has conducted a compliance audit of the grants received by CISCE Hyderabad Regional Centre from the Ministry of Human Resource Development (now Ministry of Education) for the financial year 2023-24. The audit team visited your office during February 2025.\n\nThe key findings of the audit are summarised below:\n1. Grant of Rs. 2.35 Crore was received during FY 2023-24.\n2. Expenditure of Rs. 2.12 Crore was incurred leaving unspent balance of Rs. 23.00 Lakhs.\n3. Unspent balance was not surrendered/refunded as required under GFR Rule 232(1).\n4. Utilisation Certificate was submitted with a delay of 45 days beyond the prescribed timeline.\n5. Three instances of procurement without following GEM portal were noticed.\n\nYou are requested to furnish replies to the attached audit observations within 30 days.\n\n(M. Venkateshwarlu)\nDirector of Audit",
    },
    {
        'days': 75, 'sender': 'The Billing Manager',
        'org': 'Telangana State Southern Power Distribution Company Ltd (TSSPDCL)',
        'addr': 'Corporate Office, Mint Compound, Hyderabad-500063',
        'subject': 'Electricity bill for the quarter January-March 2025 — Consumer No. HYD-4532178',
        'dept': 'FINAC', 'doc_type': 'bill', 'pages': 3, 'status': 'acknowledged',
        'mode': 'courier',
        'ocr': "TELANGANA STATE SOUTHERN POWER DISTRIBUTION COMPANY LIMITED\nBILLING SECTION\n\nBill No.: TSS/HYD/Q1-2025/78432\nConsumer No.: HYD-4532178\nBilling Period: 01.01.2025 to 31.03.2025\nDate of Issue: 05.04.2025\n\nConsumer Name: CISCE Hyderabad Regional Centre\nAddress: Plot No. 12, Banjara Hills, Road No. 3, Hyderabad-500034\nCategory: LT-II (A) — Government Office\n\nParticulars:\nPrevious Reading: 45,230 kWh\nPresent Reading: 52,180 kWh\nUnits Consumed: 6,950 kWh\n\nEnergy Charges: Rs. 48,650.00\nFixed Charges: Rs. 3,500.00\nElectricity Duty: Rs. 2,916.75\nMeter Rent: Rs. 50.00\nGross Amount: Rs. 55,116.75\n\nDue Date: 20.04.2025\nPayment Mode: Online/NEFT/Cheque in favour of TSSPDCL\n\nNote: Late payment surcharge of 1.5% per month will be applicable after due date.",
    },
    {
        'days': 72, 'sender': 'Dr. S. Ramanathan, Regional Director',
        'org': 'Indira Gandhi National Open University (IGNOU), Regional Centre Hyderabad',
        'addr': 'IGNOU Regional Centre, Nanakramguda, Hyderabad-500032',
        'subject': 'Collaboration proposal for staff development programme under Gyan Darshan scheme',
        'dept': 'HR', 'doc_type': 'correspondence', 'pages': 3, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "INDIRA GANDHI NATIONAL OPEN UNIVERSITY\nREGIONAL CENTRE, HYDERABAD\n\nRef. No.: IGNOU/RC-HYD/COLLAB/2025/089\nDated: 28.03.2025\n\nTo,\nThe Regional Director,\nCISCE Hyderabad Regional Centre, Hyderabad.\n\nSubject: Proposal for collaboration on Staff Development Programme under Gyan Darshan Scheme for FY 2025-26.\n\nDear Sir/Madam,\n\nIGNOU Regional Centre, Hyderabad proposes to collaborate with your esteemed organisation for conducting a series of staff development programmes under the Gyan Darshan scheme of the Ministry of Education.\n\nThe proposed programmes include:\n1. Certificate Programme in Office Management and Secretarial Practice (6 months)\n2. Diploma in Computer Applications for Government Officials (1 year)\n3. Short-term course on Right to Information Act, 2005 (3 months)\n\nThe programmes can be conducted at your premises during weekends. IGNOU will provide study materials, faculty, and examinations. Your office would need to provide venue and coordinate employee enrollment.\n\nKindly convey your in-principle approval at the earliest so that we may include this in our annual academic calendar.\n\n(Dr. S. Ramanathan)\nRegional Director, IGNOU Hyderabad",
    },
    {
        'days': 68, 'sender': 'Shri P.K. Sinha, Joint Secretary (Estt.)',
        'org': 'Department of Personnel and Training (DoPT), North Block, New Delhi',
        'addr': 'Room 312, North Block, New Delhi-110001',
        'subject': 'Government Order regarding implementation of modified ACP scheme for Group B & C employees',
        'dept': 'HR', 'doc_type': 'circular', 'pages': 6, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "GOVERNMENT OF INDIA\nMINISTRY OF PERSONNEL, PUBLIC GRIEVANCES AND PENSIONS\nDEPARTMENT OF PERSONNEL AND TRAINING\n\nOffice Memorandum No. 35034/3/2025-Estt.(D)\nDated: 01.04.2025\n\nSubject: Implementation of Modified Assured Career Progression (MACP) Scheme for Group B and Group C employees — Revised guidelines.\n\nThe undersigned is directed to state that in supersession of earlier orders on the subject, the competent authority has approved the following modifications to the MACP Scheme:\n\n1. Financial upgradation under MACP shall now be granted upon completion of 8, 16, and 24 years of continuous regular service.\n2. Benchmark for MACP has been relaxed from 'Very Good' to 'Good' for employees in Level-1 to Level-5.\n3. Employees who have been denied MACP on account of pending disciplinary proceedings shall be granted upgradation from the original due date upon exoneration.\n\nAll Ministries/Departments and attached/subordinate offices are requested to ensure compliance with immediate effect. Anomalies, if any, may be referred to this Department.\n\n(P.K. Sinha)\nJoint Secretary to the Government of India",
    },
    {
        'days': 65, 'sender': 'The Assessing Officer, Ward 12(3)',
        'org': 'Income Tax Department, Hyderabad',
        'addr': 'Aayakar Bhavan, Basheerbagh, Hyderabad-500004',
        'subject': 'Notice u/s 143(1) of Income Tax Act regarding TDS compliance for AY 2024-25',
        'dept': 'FINAC', 'doc_type': 'legal_notice', 'pages': 4, 'status': 'acknowledged',
        'mode': 'registered_post',
        'ocr': "INCOME TAX DEPARTMENT\nOFFICE OF THE ASSESSING OFFICER, WARD 12(3), HYDERABAD\n\nNotice No.: ITO/HYD/W12(3)/143(1)/2025/1287\nDated: 05.04.2025\nPAN: AAAGC1234R\nAY: 2024-25\n\nTo,\nThe Chief Accounts Officer,\nCISCE Hyderabad Regional Centre\n\nSubject: Intimation under Section 143(1) of the Income Tax Act, 1961 — Assessment Year 2024-25\n\nSir/Madam,\n\nWith reference to the TDS return filed by your organisation for Assessment Year 2024-25, the following discrepancies have been noticed during processing:\n\n1. Short deduction of TDS under Section 194C in respect of payments made to contractors amounting to Rs. 4,56,000/- during Q3 FY 2024-25.\n2. Late deposit of TDS for the month of November 2024 attracting interest under Section 201(1A).\n3. Mismatch between Form 26AS and TDS return filed for Q2.\n\nYou are directed to furnish your explanation/revised return within 30 days from the date of this notice, failing which, demand will be raised as per provisions of the Act.\n\n(Sd/-)\nAssessing Officer, Ward 12(3), Hyderabad",
    },
    {
        'days': 62, 'sender': 'Smt. K. Padmavathi, Director (Procurement)',
        'org': 'Central Vigilance Commission (CVC), Satarkta Bhawan, New Delhi',
        'addr': 'Satarkta Bhawan, GPO Complex, INA, New Delhi-110023',
        'subject': 'Circular on revised guidelines for procurement through GeM portal — mandatory compliance',
        'dept': 'ADMIN', 'doc_type': 'circular', 'pages': 5, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "CENTRAL VIGILANCE COMMISSION\nSATARKTA BHAWAN, NEW DELHI\n\nCircular No. CVC/PROC/2025/004\nDated: 10.04.2025\n\nSubject: Revised guidelines for procurement of goods and services through Government e-Marketplace (GeM) — Mandatory Compliance.\n\nAttention of all Ministries/Departments and organisations receiving Government grants is invited to the following revised procurement guidelines:\n\n1. All procurement of goods and services available on GeM portal must be done through GeM only. No exemption shall be granted for items listed on the portal.\n2. For items not available on GeM, a certificate from the GeM portal confirming non-availability must be obtained before initiating offline procurement.\n3. All procurement above Rs. 25,000/- must have a comparative statement of at least 3 quotations.\n4. Procurement officers must complete the GeM Orientation Course within 60 days.\n\nNon-compliance with the above guidelines will be viewed seriously and may attract vigilance proceedings. All heads of organisations are directed to ensure strict compliance.\n\n(K. Padmavathi)\nDirector (Procurement), CVC",
    },
    {
        'days': 60, 'sender': 'The Branch Manager, SBI Banjara Hills',
        'org': 'State Bank of India, Banjara Hills Branch, Hyderabad',
        'addr': 'SBI Banjara Hills Branch, Road No. 1, Hyderabad-500034',
        'subject': 'Communication regarding dormant account reactivation and updated KYC for Account No. 52014578932',
        'dept': 'FINAC', 'doc_type': 'correspondence', 'pages': 2, 'status': 'acknowledged',
        'mode': 'hand_delivery',
        'ocr': "STATE BANK OF INDIA\nBANJARA HILLS BRANCH, HYDERABAD\n\nRef: SBI/BH/ACC/2025/0341\nDate: 15.04.2025\n\nTo,\nThe Chief Accounts Officer,\nCISCE Hyderabad Regional Centre\n\nSubject: Reactivation of Dormant Savings Account No. 52014578932 and Updated KYC Requirements\n\nDear Sir/Madam,\n\nWe wish to inform you that your savings account bearing No. 52014578932 maintained at our branch has been classified as 'Dormant' due to non-operation for a period exceeding 24 months, as per RBI guidelines.\n\nTo reactivate the account, we request you to:\n1. Submit a written application for reactivation on the organisation's letterhead.\n2. Provide updated KYC documents (PAN card, Registration Certificate, Board Resolution).\n3. Make an initial transaction (deposit/withdrawal) at the branch.\n\nThe current balance in the account is Rs. 1,23,456.78. No charges will be levied for reactivation.\n\nKindly visit the branch at your earliest convenience with the above documents.\n\n(Sd/-)\nBranch Manager\nSBI, Banjara Hills, Hyderabad",
    },

    # ======================================================================
    # GROUP 2 — ARCHIVED, 30-60 days ago (10 docs)
    # ======================================================================
    {
        'days': 55, 'sender': 'Shri V. Ramakrishna, Deputy Director (Estt.)',
        'org': 'Employees Provident Fund Organisation (EPFO), Regional Office Hyderabad',
        'addr': 'EPFO Bhavan, 1-1-62, RTC X Roads, Hyderabad-500020',
        'subject': 'Annual provident fund compliance certificate and ECR filing status for FY 2024-25',
        'dept': 'FINAC', 'doc_type': 'correspondence', 'pages': 5, 'status': 'archived',
        'mode': 'registered_post',
        'ocr': "EMPLOYEES PROVIDENT FUND ORGANISATION\nMINISTRY OF LABOUR AND EMPLOYMENT, GOVERNMENT OF INDIA\nREGIONAL OFFICE, HYDERABAD\n\nRef: EPFO/RO-HYD/COMP/2025/5643\nDate: 25.04.2025\n\nTo,\nThe Establishment Head,\nCISCE Hyderabad Regional Centre\n\nSubject: Annual PF Compliance Certificate and ECR Filing Status for FY 2024-25\n\nThis is to certify that the above establishment (Code: TG/HYD/23456) has filed all monthly Electronic Challan cum Return (ECR) for the financial year 2024-25. However, the following observations are noted:\n\n1. ECR for March 2025 was filed with a delay of 7 days.\n2. PF contribution for two contractual employees was not remitted for January 2025.\n3. Annual Return (Form 3A/6A equivalent) is pending submission.\n\nYou are requested to ensure timely compliance and rectify the above discrepancies within 15 days.",
    },
    {
        'days': 52, 'sender': 'Dr. K. Srinivas, Director',
        'org': 'National Informatics Centre (NIC), Telangana State Unit',
        'addr': 'NIC, Secretariat Building, Hyderabad-500022',
        'subject': 'Implementation of IPv6 migration and cybersecurity audit requirements',
        'dept': 'IT', 'doc_type': 'circular', 'pages': 6, 'status': 'archived',
        'mode': 'hand_delivery',
        'ocr': "NATIONAL INFORMATICS CENTRE\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nTELANGANA STATE UNIT, HYDERABAD\n\nCircular No.: NIC/TS/IT-SEC/2025/021\nDate: 28.04.2025\n\nSubject: Mandatory Implementation of IPv6 Migration and Annual Cybersecurity Audit.\n\nAll government offices and affiliated organisations are hereby directed to undertake the following IT infrastructure upgrades by 30.09.2025:\n\n1. Complete migration from IPv4 to IPv6 addressing for all networked devices.\n2. Conduct STQC-empanelled cybersecurity audit of all IT assets.\n3. Deploy endpoint protection on all government-owned computing devices.\n4. Enable multi-factor authentication for all email and portal access.\n\nOrganisations may approach NIC State Unit for technical guidance and empanelled vendor details. Compliance report must be submitted to NIC by 31.10.2025.",
    },
    {
        'days': 49, 'sender': 'Shri H. Narayan, Section Officer (Training)',
        'org': 'Institute of Secretariat Training and Management (ISTM), New Delhi',
        'addr': 'ISTM, Administrative Block, JNU Campus, New Delhi-110067',
        'subject': 'Nomination for in-service training programme on e-Office implementation — May 2025 batch',
        'dept': 'HR', 'doc_type': 'correspondence', 'pages': 4, 'status': 'archived',
        'mode': 'speed_post',
        'ocr': "INSTITUTE OF SECRETARIAT TRAINING AND MANAGEMENT\nDEPARTMENT OF PERSONNEL AND TRAINING, GOVERNMENT OF INDIA\n\nRef: ISTM/TRNG/e-Office/2025/Batch-V\nDate: 01.05.2025\n\nTo,\nThe Head of Office,\nCISCE Hyderabad Regional Centre\n\nSubject: Nomination of officials for 5-day in-service training on e-Office 7.0 Implementation — May 2025 Batch.\n\nISTM is conducting a training programme on e-Office 7.0 for Section Officers and Assistants. Details:\n\nDuration: 19.05.2025 to 23.05.2025\nVenue: ISTM, JNU Campus, New Delhi\nTA/DA: As per entitlement\nMax Nominees: 2 per organisation\n\nTopics: File management, digital signatures, DAK handling, electronic noting and drafting, file tracking, and NIC cloud integration.\n\nNominations may be sent by 10.05.2025.",
    },
    {
        'days': 46, 'sender': 'Chief General Manager',
        'org': 'New India Assurance Co. Ltd., Hyderabad DO',
        'addr': 'New India Assurance, 3-6-322, Himayatnagar, Hyderabad-500029',
        'subject': 'Renewal notice for group insurance and fire insurance policies expiring on 30.06.2025',
        'dept': 'FINAC', 'doc_type': 'bill', 'pages': 3, 'status': 'archived',
        'mode': 'courier',
        'ocr': "NEW INDIA ASSURANCE COMPANY LIMITED\nDIVISIONAL OFFICE, HYDERABAD\n\nPolicy Renewal Notice\nDate: 04.05.2025\n\nTo,\nThe Accounts Officer,\nCISCE Hyderabad Regional Centre\n\nSubject: Renewal of Group Insurance Policy (No. 210200/46/2024/7865) and Fire Insurance Policy (No. 110100/46/2024/3421) expiring on 30.06.2025.\n\nDear Sir/Madam,\n\nPlease note that the following insurance policies are due for renewal:\n\n1. Group Insurance Policy: Premium Rs. 1,85,000/- (for 56 employees)\n2. Fire Insurance (Building + Contents): Premium Rs. 42,000/-\nTotal Renewal Premium: Rs. 2,27,000/-\n\nKindly ensure that the renewal premium is remitted before 25.06.2025 to avoid lapse of coverage. Cheque/NEFT in favour of 'New India Assurance Co. Ltd.' payable at Hyderabad.",
    },
    {
        'days': 43, 'sender': 'Smt. Anitha Reddy, Additional Director',
        'org': 'Directorate of Fire Services, Government of Telangana',
        'addr': 'Fire Services HQ, Barkathpura, Hyderabad-500027',
        'subject': 'Fire safety compliance inspection report and deficiency rectification directions',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 7, 'status': 'archived',
        'mode': 'registered_post',
        'ocr': "DIRECTORATE OF FIRE SERVICES\nGOVERNMENT OF TELANGANA\n\nRef: DFS/INSP/HYD/2025/0456\nDate: 07.05.2025\n\nTo,\nThe Head of Office,\nCISCE Hyderabad Regional Centre\n\nSubject: Fire Safety Compliance Inspection Report — Inspection dated 02.05.2025.\n\nAn inspection of your office premises was conducted on 02.05.2025 by the team led by Station Fire Officer, Banjara Hills Station. The following deficiencies were noticed:\n\n1. Two fire extinguishers on the second floor have expired (last refilled in 2022).\n2. Emergency exit on the ground floor is partially blocked by stored furniture.\n3. Fire alarm system on the first floor is non-functional.\n4. Evacuation plan not displayed at prominent locations.\n\nYou are directed to rectify the above deficiencies within 30 days and submit a compliance report to this office.",
    },
    {
        'days': 40, 'sender': 'Shri A.K. Saxena, CEO',
        'org': 'National Board of Accreditation (NBA), AICTE Complex, New Delhi',
        'addr': 'NBA, AICTE Complex, Vasant Kunj, New Delhi-110070',
        'subject': 'Accreditation renewal process and submission of Self-Assessment Report for 2025-26 cycle',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 8, 'status': 'archived',
        'mode': 'speed_post',
        'ocr': "NATIONAL BOARD OF ACCREDITATION\nAICTE COMPLEX, NEW DELHI\n\nRef: NBA/ACC/2025/RENEWAL/0234\nDate: 10.05.2025\n\nTo,\nThe Regional Director,\nCISCE Hyderabad Regional Centre\n\nSubject: Accreditation Renewal Process — Submission of Self-Assessment Report for 2025-26 Cycle.\n\nThe accreditation granted to your institution is due for renewal. You are requested to submit the Self-Assessment Report (SAR) through the NBA portal by 31.07.2025. The SAR must include updated data on governance, infrastructure, academic performance, and stakeholder feedback.\n\nTeam visit will be scheduled post-SAR verification. Registration fee of Rs. 3,00,000/- is payable online.",
    },
    {
        'days': 37, 'sender': 'The Nodal Officer, e-Waste Management',
        'org': 'Telangana State Pollution Control Board (TSPCB)',
        'addr': 'TSPCB, Paryavaran Bhavan, A.P. Housing Board Colony, Hyderabad-500004',
        'subject': 'Annual return filing requirement for e-Waste disposal under E-Waste Management Rules 2022',
        'dept': 'IT', 'doc_type': 'correspondence', 'pages': 3, 'status': 'archived',
        'mode': 'courier',
        'ocr': "TELANGANA STATE POLLUTION CONTROL BOARD\nPARYAVARAN BHAVAN, HYDERABAD\n\nRef: TSPCB/e-Waste/2025/0891\nDate: 13.05.2025\n\nTo,\nThe IT Head,\nCISCE Hyderabad Regional Centre\n\nSubject: Annual Return for E-Waste Disposal under E-Waste (Management) Rules, 2022.\n\nAs per Rule 16 of the E-Waste (Management) Rules, 2022, all bulk consumers generating more than 100 kg of e-waste annually are required to file an annual return in Form-3 to the State Pollution Control Board.\n\nYou are directed to file the annual return for FY 2024-25 by 30.06.2025 along with details of authorised dismantlers/recyclers used for disposal.",
    },
    {
        'days': 34, 'sender': 'Joint Director (Accounts)',
        'org': 'Controller General of Accounts (CGA), Ministry of Finance',
        'addr': 'CGA, Mahalekha Niyantrak Bhawan, INA Colony, New Delhi-110023',
        'subject': 'Quarterly expenditure report submission in PFMS format for Q4 FY 2024-25',
        'dept': 'FINAC', 'doc_type': 'circular', 'pages': 4, 'status': 'archived',
        'mode': 'speed_post',
        'ocr': "CONTROLLER GENERAL OF ACCOUNTS\nMINISTRY OF FINANCE, GOVERNMENT OF INDIA\n\nOM No. CGA/PFMS/Q4/2025/456\nDate: 16.05.2025\n\nSubject: Submission of Quarterly Expenditure Report in PFMS Format for Q4 (January-March 2025).\n\nAll Drawing and Disbursing Officers (DDOs) are directed to submit the quarterly expenditure report for Q4 FY 2024-25 in the prescribed PFMS format through the Public Financial Management System portal by 15.06.2025.\n\nThe report must reconcile with the figures reflected in the monthly accounts and any discrepancy must be explained. Failure to submit the report within the stipulated time may result in withholding of grant releases for FY 2025-26.",
    },
    {
        'days': 31, 'sender': 'Shri G.V. Krishna Rao, Commissioner',
        'org': 'Office of the Commissioner for Persons with Disabilities, Telangana',
        'addr': 'D.No. 5-10-193, CCPD Office, Hyderabad-500004',
        'subject': 'Compliance report on accessibility audit and implementation of RPwD Act 2016 provisions',
        'dept': 'LEGAL', 'doc_type': 'correspondence', 'pages': 5, 'status': 'archived',
        'mode': 'registered_post',
        'ocr': "OFFICE OF THE COMMISSIONER FOR PERSONS WITH DISABILITIES\nGOVERNMENT OF TELANGANA\n\nRef: CCPD/TS/ACC/2025/0134\nDate: 19.05.2025\n\nTo,\nThe Head of Office,\nCISCE Hyderabad Regional Centre\n\nSubject: Compliance Report on Accessibility Audit and Implementation of Rights of Persons with Disabilities Act, 2016.\n\nAs per Section 44 and 45 of the RPwD Act, 2016, all government establishments are mandated to ensure accessibility in their buildings, ICT infrastructure, and services. You are directed to submit a compliance report covering:\n\n1. Physical accessibility (ramps, accessible toilets, Braille signage).\n2. Website accessibility as per GIGW Guidelines.\n3. Reservation in posts for PwD candidates.\n4. Appointment of Liaison Officer for PwD matters.\n\nReport must be submitted by 30.06.2025.",
    },

    # ======================================================================
    # GROUP 3 — ACKNOWLEDGED, 15-30 days ago (15 docs)
    # ======================================================================
    {
        'days': 28, 'sender': 'Shri R.K. Trivedi, CPIO',
        'org': 'Central Information Commission (CIC), August Kranti Bhawan, New Delhi',
        'addr': 'CIC, Baba Kharak Singh Marg, New Delhi-110001',
        'subject': 'RTI Appeal No. CIC/SA/A/2025/001234 — directions for furnishing information',
        'dept': 'LEGAL', 'doc_type': 'legal_notice', 'pages': 4, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "CENTRAL INFORMATION COMMISSION\nAUGUST KRANTI BHAWAN, NEW DELHI\n\nDecision No.: CIC/SA/A/2025/001234\nDate: 22.05.2025\n\nAppellant: Shri Vijay Mohan Reddy\nRespondent: CPIO, CISCE Hyderabad Regional Centre\n\nThe Commission has considered the Second Appeal filed by the appellant against the order of the First Appellate Authority. The Commission directs the CPIO to furnish the following information within 15 days:\n\n1. Complete list of contractual employees hired during 2023-24 with qualification details.\n2. Copy of the recruitment policy for contractual positions.\n3. Details of expenditure incurred on outsourced services.\n\nPenalty proceedings under Section 20 are kept in abeyance pending compliance.",
    },
    {
        'days': 27, 'sender': 'The Divisional Manager',
        'org': 'Life Insurance Corporation of India, Hyderabad Divisional Office',
        'addr': 'LIC, Divisional Office, Ashok Nagar, Hyderabad-500020',
        'subject': 'Group Savings Linked Insurance Scheme — premium notice for policy year 2025-26',
        'dept': 'FINAC', 'doc_type': 'bill', 'pages': 2, 'status': 'acknowledged',
        'mode': 'courier',
        'ocr': "LIFE INSURANCE CORPORATION OF INDIA\nDIVISIONAL OFFICE, HYDERABAD\n\nRef: LIC/HYD/GSLI/2025/PRN-0456\nDate: 23.05.2025\n\nTo,\nThe DDO/Accounts Officer,\nCISCE Hyderabad Regional Centre\n\nSubject: Group Savings Linked Insurance (GSLI) Scheme — Premium Notice for Policy Year 2025-26.\n\nPolicy No.: HYD-GSLI-987654\nNo. of Members: 48\nAnnual Premium: Rs. 96,000/- (@ Rs. 2,000 per member)\nDue Date: 01.07.2025\n\nKindly ensure timely remittance of the premium to maintain continuity of coverage.",
    },
    {
        'days': 25, 'sender': 'Smt. Padma Lokesh, Director (Recruitment)',
        'org': 'Staff Selection Commission (SSC), Southern Region, Chennai',
        'addr': 'SSC (SR), E.V.K. Sampath Salai, Vepery, Chennai-600007',
        'subject': 'Vacancy report requisition for CGL 2025 examination — submission of Form-V',
        'dept': 'HR', 'doc_type': 'correspondence', 'pages': 3, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "STAFF SELECTION COMMISSION\nSOUTHERN REGION, CHENNAI\n\nRef: SSC(SR)/CGL-2025/VAC/0789\nDate: 25.05.2025\n\nTo,\nThe Head of Office/Cadre Controlling Authority,\nCISCE Hyderabad Regional Centre\n\nSubject: Requisition of Vacancies for Combined Graduate Level (CGL) Examination, 2025 — Submission of Form-V.\n\nKindly submit the details of anticipated vacancies for the following posts for CGL 2025 recruitment:\n1. Assistants (Group 'B')\n2. Upper Division Clerks (Group 'C')\n3. Tax Assistants (Group 'C')\n\nForm-V must be submitted through the SSC portal by 15.06.2025. Year-wise break-up of vacancies with reservation roster position must be furnished.",
    },
    {
        'days': 24, 'sender': 'Shri M. Ashok Kumar, Director',
        'org': 'National Productivity Council (NPC), Chennai',
        'addr': 'NPC, Institutional Area, Uthamar Gandhi Salai, Chennai-600025',
        'subject': 'Circular on National Productivity Week celebrations and essay competition 2025',
        'dept': 'HR', 'doc_type': 'circular', 'pages': 3, 'status': 'acknowledged',
        'mode': 'courier',
        'ocr': "NATIONAL PRODUCTIVITY COUNCIL\n(An Autonomous Body under DPIIT, Ministry of Commerce & Industry)\n\nCircular No.: NPC/NPW/2025/078\nDate: 26.05.2025\n\nSubject: Celebration of National Productivity Week (12-18 February 2026) and Essay Competition.\n\nAll government offices are requested to celebrate National Productivity Week and encourage employees to participate in the essay competition on the theme 'Digital Transformation for Enhanced Productivity in Government Services.' Cash prizes of Rs. 25,000, Rs. 15,000, and Rs. 10,000 will be awarded. Entries to be submitted by 31.01.2026.",
    },
    {
        'days': 23, 'sender': 'The General Manager (Systems)',
        'org': 'BSNL, Telangana Telecom Circle, Hyderabad',
        'addr': 'BSNL, Telephone Bhavan, Nampally, Hyderabad-500001',
        'subject': 'Migration of existing MPLS VPN connections to SD-WAN — schedule and requirements',
        'dept': 'IT', 'doc_type': 'correspondence', 'pages': 5, 'status': 'acknowledged',
        'mode': 'hand_delivery',
        'ocr': "BHARAT SANCHAR NIGAM LIMITED\nTELANGANA TELECOM CIRCLE, HYDERABAD\n\nRef: BSNL/TS/ENT/SD-WAN/2025/0234\nDate: 27.05.2025\n\nTo,\nThe IT Administrator,\nCISCE Hyderabad Regional Centre\n\nSubject: Migration from MPLS VPN to SD-WAN Technology — Schedule and Requirements.\n\nAs part of BSNL's enterprise network modernisation initiative, your existing 2 Mbps MPLS VPN connectivity (CUG No. HYD-ENT-5678) will be upgraded to SD-WAN based broadband. Benefits include higher bandwidth (100 Mbps), improved reliability, and integrated security.\n\nScheduled migration date: 15.07.2025\nDowntime: 4-6 hours\nRequirements: Dedicated rack space for CPE device and UPS backup.",
    },
    {
        'days': 22, 'sender': 'Controller of Examinations',
        'org': 'CISCE (Council for Indian School Certificate Examinations), New Delhi HQ',
        'addr': 'CISCE, Pragati House, Third Floor, 47-48, Nehru Place, New Delhi-110019',
        'subject': 'Annual report submission requirements and regional performance statistics for ICSE/ISC 2025',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 6, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS\nPRAGATI HOUSE, NEW DELHI\n\nRef: CISCE/HQ/ARC/2025/0345\nDate: 28.05.2025\n\nTo,\nThe Regional Director,\nCISCE Hyderabad Regional Centre\n\nSubject: Submission of Annual Regional Report and Performance Statistics for ICSE and ISC Examinations 2025.\n\nThe Regional Director is requested to submit the Annual Regional Report for 2025 covering:\n1. Affiliated schools statistics (new affiliations, de-affiliations, total count).\n2. ICSE (Class X) and ISC (Class XII) examination results summary.\n3. Infrastructure inspection reports of affiliated schools.\n4. Grievance redressal data.\n5. Budget utilisation summary for FY 2024-25.\n\nReport must be submitted by 30.06.2025 in the prescribed format.",
    },
    {
        'days': 21, 'sender': 'Shri T. Venkat Rao, Deputy Director',
        'org': 'Directorate General of Supplies and Disposals (DGS&D)',
        'addr': 'DGS&D, Supply Depot, Karkhana, Secunderabad-500015',
        'subject': 'Rate contract for supply of office furniture — Annual indent submission for 2025-26',
        'dept': 'ADMIN', 'doc_type': 'tender', 'pages': 4, 'status': 'acknowledged',
        'mode': 'courier',
        'ocr': "DIRECTORATE GENERAL OF SUPPLIES AND DISPOSALS\nMINISTRY OF COMMERCE AND INDUSTRY, GOVERNMENT OF INDIA\n\nRef: DGS&D/RC/FURN/2025-26/0567\nDate: 29.05.2025\n\nTo,\nThe Head of Office / Indenting Officer,\nCISCE Hyderabad Regional Centre\n\nSubject: Rate Contract for Supply of Office Furniture — Annual Indent Submission for FY 2025-26.\n\nThe following Rate Contracts for office furniture are in force for FY 2025-26:\n\nRC No. 1: Steel Almirahs (4 shelves) — Rs. 12,500/- per unit\nRC No. 2: Executive Desks (with drawers) — Rs. 18,000/- per unit\nRC No. 3: Revolving Chairs (Medium Back) — Rs. 8,500/- per unit\n\nIndents may be placed through GeM or by submitting Form DGS&D-257 to this office before 31.07.2025.",
    },
    {
        'days': 20, 'sender': 'Shri K. Bhaskar, Regional PF Commissioner',
        'org': 'EPFO, Regional Office, Hyderabad',
        'addr': 'EPFO Bhavan, RTC X Roads, Hyderabad-500020',
        'subject': 'Circular on revised interest rate for EPF deposits — 8.25% for FY 2024-25',
        'dept': 'FINAC', 'doc_type': 'circular', 'pages': 2, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "EMPLOYEES PROVIDENT FUND ORGANISATION\nREGIONAL OFFICE, HYDERABAD\n\nCircular No.: EPFO/RO-HYD/INT/2025/012\nDate: 30.05.2025\n\nSubject: Rate of Interest on EPF Deposits for FY 2024-25 — 8.25%.\n\nThe Central Board of Trustees, EPF has recommended an interest rate of 8.25% for the FY 2024-25, approved by the Ministry of Finance. All establishments are directed to credit the interest amount to members' accounts and ensure correct calculation in the annual statement of accounts (Passbook).",
    },
    {
        'days': 19, 'sender': 'Dr. P. Suresh, Joint Director',
        'org': 'Indian Computer Emergency Response Team (CERT-In), MeitY',
        'addr': 'CERT-In, Electronics Niketan, CGO Complex, New Delhi-110003',
        'subject': 'Advisory on critical vulnerabilities in government email systems — immediate patching required',
        'dept': 'IT', 'doc_type': 'circular', 'pages': 3, 'status': 'acknowledged',
        'mode': 'speed_post',
        'ocr': "INDIAN COMPUTER EMERGENCY RESPONSE TEAM (CERT-In)\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\n\nAdvisory No.: CERT-In/VULN/2025/054\nDate: 31.05.2025\nClassification: URGENT\n\nSubject: Critical Vulnerabilities in Government Email Systems — Immediate Patching Required.\n\nCERT-In has identified critical vulnerabilities (CVE-2025-XXXX) in the NIC email system (email.gov.in) that could allow remote code execution and data exfiltration. All government organisations are directed to:\n\n1. Immediately update email client software to the latest version.\n2. Reset all administrative passwords.\n3. Enable two-factor authentication.\n4. Report any suspicious activity to incident@cert-in.org.in.\n\nCompliance report must be submitted within 7 days.",
    },
    {
        'days': 18, 'sender': 'Smt. Jayashree Iyer, Under Secretary',
        'org': 'Ministry of Education, Department of Higher Education',
        'addr': 'Shastri Bhawan, Dr. Rajendra Prasad Road, New Delhi-110001',
        'subject': 'Disbursement of annual grant-in-aid for FY 2025-26 — first instalment release order',
        'dept': 'FINAC', 'doc_type': 'correspondence', 'pages': 3, 'status': 'acknowledged',
        'mode': 'registered_post',
        'ocr': "MINISTRY OF EDUCATION\nDEPARTMENT OF HIGHER EDUCATION\nGOVERNMENT OF INDIA\n\nOM No.: F.5-23/2025-Dn.III\nDate: 01.06.2025\n\nTo,\nThe Regional Director,\nCISCE Hyderabad Regional Centre\n\nSubject: Release of First Instalment of Grant-in-Aid for FY 2025-26.\n\nSanction is hereby accorded for the release of Rs. 1,15,00,000/- (Rupees One Crore Fifteen Lakhs Only) being the first instalment of Grant-in-Aid for FY 2025-26, subject to the following conditions:\n\n1. Submission of Utilisation Certificate for previous year's grant.\n2. Audited accounts for FY 2024-25.\n3. Physical and financial progress report.\n\nThe amount will be transferred through PFMS to the designated bank account.",
    },
    {
        'days': 17, 'sender': 'Shri D. Anurag, Commissioner',
        'org': 'Goods and Services Tax (GST) Commissionerate, Hyderabad',
        'addr': 'GST Bhavan, Nampally, Hyderabad-500001',
        'subject': 'Clarification on GST applicability on fees collected from affiliated schools',
        'dept': 'FINAC', 'doc_type': 'legal_notice', 'pages': 4, 'status': 'acknowledged',
        'mode': 'hand_delivery',
        'ocr': "OFFICE OF THE COMMISSIONER OF GST\nHYDERABAD COMMISSIONERATE\n\nRef: GST/HYD/CLARIFY/2025/0678\nDate: 02.06.2025\n\nTo,\nThe Accounts Officer,\nCISCE Hyderabad Regional Centre\n\nSubject: Clarification on GST Applicability on Fees Collected from Affiliated Schools.\n\nIn response to your letter dated 15.05.2025 seeking clarification on GST applicability on various fees collected from affiliated schools, the following is clarified:\n\n1. Affiliation fees: Exempt under Notification 12/2017-CT(Rate) Sr. No. 66 as education service.\n2. Examination fees: Exempt.\n3. Infrastructure inspection charges: Taxable at 18% if charged as consultancy.\n4. Late fee/penalty: Taxable at 18%.\n\nYou are advised to register separately for taxable services and file returns accordingly.",
    },
    {
        'days': 16, 'sender': 'The General Manager, HUDA',
        'org': 'Hyderabad Metropolitan Development Authority (HMDA)',
        'addr': 'HMDA, Elarathota, Tank Bund Road, Hyderabad-500080',
        'subject': 'Notice regarding property tax reassessment for office premises at Banjara Hills',
        'dept': 'ADMIN', 'doc_type': 'legal_notice', 'pages': 3, 'status': 'acknowledged',
        'mode': 'registered_post',
        'ocr': "HYDERABAD METROPOLITAN DEVELOPMENT AUTHORITY\n\nRef: HMDA/PT/REASSESS/2025/04567\nDate: 03.06.2025\n\nTo,\nThe Head of Office,\nCISCE Hyderabad Regional Centre,\nPlot No. 12, Banjara Hills, Hyderabad\n\nSubject: Property Tax Reassessment for Office Premises — Assessment Year 2025-26.\n\nAs per the revised property tax slab rates notified by GHMC w.e.f. 01.04.2025, your office premises has been reassessed. The revised annual property tax is Rs. 2,45,000/- (previously Rs. 1,87,000/-).\n\nYou may file objections within 30 days. Payment of first half-year tax is due by 30.06.2025.",
    },
    {
        'days': 15, 'sender': 'Shri N. Raghavendra, Section Officer',
        'org': 'Central Board of Secondary Education (CBSE), Regional Office Hyderabad',
        'addr': 'CBSE, H.No. 8-3-945/10, Ameerpet, Hyderabad-500073',
        'subject': 'Inter-board coordination meeting for examination reforms — invitation for 25.06.2025',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 2, 'status': 'acknowledged',
        'mode': 'courier',
        'ocr': "CENTRAL BOARD OF SECONDARY EDUCATION\nREGIONAL OFFICE, HYDERABAD\n\nRef: CBSE/RO-HYD/COORD/2025/056\nDate: 04.06.2025\n\nTo,\nThe Regional Director,\nCISCE Hyderabad Regional Centre\n\nSubject: Inter-Board Coordination Meeting on Examination Reforms — 25.06.2025.\n\nA coordination meeting of all examination boards operating in Telangana is being convened to discuss reforms in examination processes, anti-malpractice measures, and digital evaluation. Your participation or that of a senior nominee is requested.\n\nDate: 25.06.2025 at 11:00 AM\nVenue: CBSE Regional Office, Ameerpet.\n\nAgenda will be circulated separately.",
    },

    # ======================================================================
    # GROUP 4 — NOTIFIED, 5-15 days ago, within SLA (10 docs)
    # ======================================================================
    {
        'days': 14, 'sender': 'Dr. V. Subrahmanyam, Secretary',
        'org': 'University Grants Commission (UGC), Bahadur Shah Zafar Marg, New Delhi',
        'addr': 'UGC, Bahadur Shah Zafar Marg, New Delhi-110002',
        'subject': 'Implementation of National Education Policy 2020 — progress report submission guidelines',
        'dept': 'ADMIN', 'doc_type': 'circular', 'pages': 8, 'status': 'notified',
        'mode': 'speed_post',
        'ocr': "UNIVERSITY GRANTS COMMISSION\n\nCircular No.: UGC/NEP/2025/023\nDate: 05.06.2025\n\nSubject: Implementation of National Education Policy 2020 — Progress Report.\n\nAll educational bodies and affiliated examination boards are directed to submit a detailed progress report on NEP 2020 implementation covering multidisciplinary education, credit framework, skill integration, and digital initiatives. Report to be submitted by 31.08.2025.",
    },
    {
        'days': 13, 'sender': 'Shri P.V. Rao, Deputy Commissioner',
        'org': 'Customs and Central Excise Department, Hyderabad Zone',
        'addr': 'Custom House, 3-5-874, Hyderguda, Hyderabad-500029',
        'subject': 'Customs duty exemption certificate renewal for imported examination equipment',
        'dept': 'FINAC', 'doc_type': 'correspondence', 'pages': 4, 'status': 'notified',
        'mode': 'courier',
        'ocr': "OFFICE OF THE COMMISSIONER OF CUSTOMS\nHYDERABAD ZONE\n\nRef: CUST/HYD/EXEMPT/2025/0345\nDate: 06.06.2025\n\nSubject: Renewal of Customs Duty Exemption Certificate for Imported Examination Processing Equipment.\n\nYour exemption certificate (No. EXM-2023-0456) for imported scanning and evaluation equipment is expiring on 30.09.2025. You are required to submit the renewal application with updated utilisation certificate, import register, and end-use certificate by 31.07.2025.",
    },
    {
        'days': 12, 'sender': 'Smt. Rekha Sharma, Joint Secretary',
        'org': 'National Commission for Women (NCW), Jasola, New Delhi',
        'addr': 'NCW, Plot No. 21, FC-33, Jasola Institutional Area, New Delhi-110025',
        'subject': 'Compliance report on implementation of POSH Act 2013 and ICC constitution',
        'dept': 'HR', 'doc_type': 'correspondence', 'pages': 3, 'status': 'notified',
        'mode': 'speed_post',
        'ocr': "NATIONAL COMMISSION FOR WOMEN\n\nRef: NCW/POSH/COMP/2025/0891\nDate: 07.06.2025\n\nSubject: Compliance Report under the Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013.\n\nAll government establishments with 10 or more employees are directed to submit the annual compliance report under the POSH Act for the calendar year 2024. The report must include details of the Internal Complaints Committee, number of complaints received, disposed, and pending. Submission deadline: 30.06.2025.",
    },
    {
        'days': 11, 'sender': 'Shri A.K. Chatterjee, CGM',
        'org': 'Reserve Bank of India (RBI), Hyderabad Regional Office',
        'addr': 'RBI, 6-1-56, Khairatabad, Hyderabad-500004',
        'subject': 'Updated KYC norms for institutional accounts — compliance by September 2025',
        'dept': 'FINAC', 'doc_type': 'circular', 'pages': 5, 'status': 'notified',
        'mode': 'registered_post',
        'ocr': "RESERVE BANK OF INDIA\nHYDERABAD REGIONAL OFFICE\n\nCircular No.: RBI/HYD/KYC/2025/034\nDate: 08.06.2025\n\nSubject: Updated KYC Norms for Institutional Accounts — Compliance Requirement.\n\nAs per revised RBI guidelines dated 15.05.2025, all institutional bank accounts must be updated with Video KYC or in-person verification by 30.09.2025. Documents required: Updated Registration Certificate, Board Resolution, PAN, and authorised signatories list with specimen signatures.",
    },
    {
        'days': 10, 'sender': 'The Station Director',
        'org': 'All India Radio (AIR), Hyderabad Station',
        'addr': 'AIR, Nampally, Hyderabad-500001',
        'subject': 'Broadcast time slot allocation for educational awareness programme — July 2025',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 2, 'status': 'notified',
        'mode': 'hand_delivery',
        'ocr': "ALL INDIA RADIO\nHYDERABAD STATION\n\nRef: AIR/HYD/EDUC/2025/078\nDate: 09.06.2025\n\nSubject: Broadcast Time Slot for Educational Awareness Programme — July 2025.\n\nFollowing your request for broadcast time for an educational awareness programme on examination reforms, a 15-minute slot has been tentatively allocated on every Sunday during July 2025 from 10:00 AM to 10:15 AM on the Vividh Bharati channel. Please confirm your acceptance and provide content scripts by 25.06.2025.",
    },
    {
        'days': 9, 'sender': 'Shri Ramesh Chandra, Director',
        'org': 'Directorate of Printing, Government of India, Nilokheri',
        'addr': 'Govt. of India Press, Nilokheri, Karnal, Haryana-132117',
        'subject': 'Annual indent for printing of examination stationery and confidential material — 2025-26',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 4, 'status': 'notified',
        'mode': 'speed_post',
        'ocr': "DIRECTORATE OF PRINTING\nGOVERNMENT OF INDIA PRESS, NILOKHERI\n\nRef: DOP/NKR/IND/2025-26/0345\nDate: 10.06.2025\n\nSubject: Annual Indent for Printing of Examination Stationery and Confidential Material — FY 2025-26.\n\nYou are requested to submit your annual indent for printing of examination-related stationery (answer booklets, OMR sheets, admit cards, certificates) and confidential material (question papers, evaluation guidelines) for FY 2025-26 by 15.07.2025. Indent must include specifications, quantity, and delivery schedule.",
    },
    {
        'days': 8, 'sender': 'Dr. Meenakshi Sundaram, Director',
        'org': 'Indian Statistical Institute (ISI), Hyderabad Centre',
        'addr': 'ISI, Street No. 8, Habsiguda, Hyderabad-500007',
        'subject': 'Proposal for statistical analysis of regional examination data — MoU for research collaboration',
        'dept': 'IT', 'doc_type': 'correspondence', 'pages': 5, 'status': 'notified',
        'mode': 'courier',
        'ocr': "INDIAN STATISTICAL INSTITUTE\nHYDERABAD CENTRE\n\nRef: ISI/HYD/COLLAB/2025/034\nDate: 11.06.2025\n\nSubject: Proposal for Statistical Analysis of Regional Examination Data — MoU for Research Collaboration.\n\nISI Hyderabad proposes a research collaboration for advanced statistical analysis of ICSE/ISC examination data including trend analysis, difficulty index computation, item response theory modelling, and predictive analytics for student performance. Draft MoU is enclosed for your consideration.",
    },
    {
        'days': 7, 'sender': 'Shri K.L.N. Reddy, Superintendent of Police',
        'org': 'Special Protection Group, Telangana Police',
        'addr': 'SPG Office, Saifabad, Hyderabad-500004',
        'subject': 'Security clearance and background verification report for newly recruited staff',
        'dept': 'HR', 'doc_type': 'correspondence', 'pages': 6, 'status': 'notified',
        'mode': 'registered_post',
        'ocr': "OFFICE OF THE SUPERINTENDENT OF POLICE\nSPECIAL PROTECTION GROUP, TELANGANA POLICE\n\nRef: SPG/TS/BV/2025/0567\nDate: 12.06.2025\n\nSubject: Security Clearance and Background Verification Report for Newly Recruited Staff.\n\nWith reference to your letter dated 25.05.2025, the background verification for the following 5 newly recruited employees has been completed. Reports are enclosed. Three candidates have been cleared. Two require further verification regarding address proof discrepancies. Please furnish additional documents within 15 days.",
    },
    {
        'days': 6, 'sender': 'The Managing Director',
        'org': 'National Small Industries Corporation (NSIC), Hyderabad Branch',
        'addr': 'NSIC, Industrial Estate, Balanagar, Hyderabad-500037',
        'subject': 'Registration renewal for procurement from MSMEs under Public Procurement Policy',
        'dept': 'FINAC', 'doc_type': 'correspondence', 'pages': 3, 'status': 'notified',
        'mode': 'courier',
        'ocr': "NATIONAL SMALL INDUSTRIES CORPORATION LIMITED\nHYDERABAD BRANCH\n\nRef: NSIC/HYD/PPP/2025/0123\nDate: 13.06.2025\n\nSubject: Registration Renewal under Public Procurement Policy for MSMEs.\n\nAs per the Public Procurement Policy for Micro and Small Enterprises Order, 2012, all CPSEs and government bodies are mandated to procure a minimum of 25% from MSMEs. Your registration for procurement from MSMEs is due for renewal. Please submit the annual procurement report and updated MSME vendor list by 31.07.2025.",
    },
    {
        'days': 5, 'sender': 'Shri Vikram Mehta, Additional Secretary',
        'org': 'Ministry of Labour and Employment, Shram Shakti Bhawan, New Delhi',
        'addr': 'Shram Shakti Bhawan, Rafi Marg, New Delhi-110001',
        'subject': 'Implementation of new labour codes — transition from old acts to consolidated codes',
        'dept': 'LEGAL', 'doc_type': 'circular', 'pages': 10, 'status': 'notified',
        'mode': 'speed_post',
        'ocr': "MINISTRY OF LABOUR AND EMPLOYMENT\nGOVERNMENT OF INDIA\n\nOM No.: S-32012/1/2025-WC\nDate: 14.06.2025\n\nSubject: Implementation of New Labour Codes — Transition from Existing Labour Acts to Consolidated Labour Codes.\n\nAll establishments are directed to prepare for the implementation of the four new Labour Codes effective from 01.10.2025:\n1. Code on Wages, 2019\n2. Industrial Relations Code, 2020\n3. Code on Social Security, 2020\n4. Occupational Safety, Health and Working Conditions Code, 2020\n\nHR departments must review existing employment contracts, standing orders, and internal policies for alignment. Transition workshops will be conducted by Regional Labour Commissioners.",
    },

    # ======================================================================
    # GROUP 5 — ESCALATED, 3-7 days ago, SLA breached (5 docs)
    # ======================================================================
    {
        'days': 7, 'sender': 'Shri B.V. Raghunath, Chief Accounts Officer',
        'org': 'Defence Accounts Department, Secunderabad',
        'addr': 'CDA (Funds), Dakshin Marg, Secunderabad-500009',
        'subject': 'Urgent reconciliation of inter-departmental transfer payments for Q4 FY 2024-25',
        'dept': 'FINAC', 'doc_type': 'correspondence', 'pages': 5, 'status': 'escalated',
        'mode': 'hand_delivery',
        'ocr': "DEFENCE ACCOUNTS DEPARTMENT\nCONTROLLER OF DEFENCE ACCOUNTS (FUNDS)\nSECUNDERABAD\n\nRef: CDA(F)/SEC/RECON/2025/0789\nDate: 12.06.2025\nClassification: URGENT\n\nSubject: Urgent Reconciliation of Inter-Departmental Transfer Payments for Q4 FY 2024-25.\n\nDiscrepancies amounting to Rs. 3,45,000/- have been noticed in the inter-departmental transfer payments for Q4. You are urgently requested to reconcile the figures and furnish supporting vouchers within 7 days. Non-compliance will be reported to the Controller General of Accounts.",
    },
    {
        'days': 6, 'sender': 'The Registrar of Companies',
        'org': 'Ministry of Corporate Affairs, ROC Hyderabad',
        'addr': 'ROC Office, 2nd Floor, CPWD Complex, Kendriya Sadan, Sultan Bazar, Hyderabad-500095',
        'subject': 'Show cause notice for delay in filing annual returns under Section 92 of Companies Act',
        'dept': 'LEGAL', 'doc_type': 'legal_notice', 'pages': 3, 'status': 'escalated',
        'mode': 'registered_post',
        'ocr': "OFFICE OF THE REGISTRAR OF COMPANIES\nMINISTRY OF CORPORATE AFFAIRS\nHYDERABAD, TELANGANA\n\nSCN No.: ROC/HYD/SCN/2025/0456\nDate: 13.06.2025\n\nSubject: Show Cause Notice for Delay in Filing Annual Returns under Section 92 of the Companies Act, 2013.\n\nIt has been noticed that the annual return for FY 2023-24 has not been filed within the prescribed time limit. You are directed to show cause within 15 days why prosecution proceedings under Section 92(5) should not be initiated. Additional fee of Rs. 100/- per day of delay is applicable.",
    },
    {
        'days': 5, 'sender': 'Smt. P. Anuradha, Chief Engineer',
        'org': 'Hyderabad Metropolitan Water Supply and Sewerage Board (HMWSSB)',
        'addr': 'HMWSSB, Khairatabad, Hyderabad-500004',
        'subject': 'Mandatory water audit report and rainwater harvesting compliance — HMWSSB regulation',
        'dept': 'ADMIN', 'doc_type': 'legal_notice', 'pages': 4, 'status': 'escalated',
        'mode': 'courier',
        'ocr': "HYDERABAD METROPOLITAN WATER SUPPLY AND SEWERAGE BOARD\n\nRef: HMWSSB/CE/WA/2025/0234\nDate: 14.06.2025\n\nSubject: Mandatory Water Audit Report and Rainwater Harvesting Compliance.\n\nAs per HMWSSB regulations, all commercial and institutional consumers with monthly consumption exceeding 50,000 litres are required to submit an annual water audit report and proof of rainwater harvesting installation. Your office has not submitted the report for FY 2024-25. Non-compliance may result in penal charges on your water bill.",
    },
    {
        'days': 4, 'sender': 'Dr. S.K. Misra, Scientist-E',
        'org': 'Ministry of Environment, Forest and Climate Change (MoEFCC)',
        'addr': 'Indira Paryavaran Bhawan, Jor Bagh Road, New Delhi-110003',
        'subject': 'Environmental compliance report under Solid Waste Management Rules 2016 — overdue',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 3, 'status': 'escalated',
        'mode': 'speed_post',
        'ocr': "MINISTRY OF ENVIRONMENT, FOREST AND CLIMATE CHANGE\nGOVERNMENT OF INDIA\n\nRef: MoEFCC/SWM/COMP/2025/0678\nDate: 15.06.2025\n\nSubject: Environmental Compliance under Solid Waste Management Rules, 2016 — Overdue Report.\n\nYour office has not submitted the annual environmental compliance report covering solid waste segregation, e-waste disposal, and hazardous waste management as mandated under SWM Rules 2016. Immediate submission is required. Failure to comply will attract penalties under Section 15 of the Environment Protection Act, 1986.",
    },
    {
        'days': 3, 'sender': 'Chief General Manager (IT)',
        'org': 'Securities and Exchange Board of India (SEBI), Hyderabad',
        'addr': 'SEBI, 3rd Floor, Jade Arcade, Banjara Hills, Hyderabad-500034',
        'subject': 'CERT-In incident report pending — cybersecurity breach notification compliance',
        'dept': 'IT', 'doc_type': 'legal_notice', 'pages': 2, 'status': 'escalated',
        'mode': 'hand_delivery',
        'ocr': "SECURITIES AND EXCHANGE BOARD OF INDIA\nHYDERABAD LOCAL OFFICE\n\nRef: SEBI/HYD/IT-SEC/2025/0123\nDate: 16.06.2025\nClassification: CONFIDENTIAL\n\nSubject: CERT-In Incident Report Pending — Cybersecurity Breach Notification Compliance.\n\nAs per CERT-In Directions of 28.04.2022, all government entities must report cybersecurity incidents within 6 hours. Our records indicate that the phishing incident reported on 10.06.2025 has not been followed up with a detailed incident report. Please submit the report immediately.",
    },

    # ======================================================================
    # GROUP 6 — ROUTED, 2-4 days ago (5 docs)
    # ======================================================================
    {
        'days': 4, 'sender': 'Shri P. Chandra Sekhar, DG',
        'org': 'National Assessment and Accreditation Council (NAAC), Bengaluru',
        'addr': 'NAAC, P.O. Box No. 1075, Nagarbhavi, Bengaluru-560072',
        'subject': 'Data submission requirements for institutional ranking under NIRF framework 2026',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 6, 'status': 'routed',
        'mode': 'courier',
        'ocr': "NATIONAL ASSESSMENT AND ACCREDITATION COUNCIL\nBENGALURU\n\nRef: NAAC/NIRF/2026/DATA/0456\nDate: 15.06.2025\n\nSubject: Data Submission for NIRF 2026 Ranking.\n\nAll participating institutions are requested to submit data in the NIRF portal covering teaching-learning, research, graduation outcomes, outreach, inclusion, and perception parameters. Deadline: 31.08.2025.",
    },
    {
        'days': 3, 'sender': 'The Chief Manager (Credit)',
        'org': 'Punjab National Bank (PNB), Hyderabad Region',
        'addr': 'PNB Regional Office, Ashok Nagar, Hyderabad-500020',
        'subject': 'Fixed deposit maturity notification — Rs. 25 lakhs maturing on 30.06.2025',
        'dept': 'FINAC', 'doc_type': 'correspondence', 'pages': 2, 'status': 'routed',
        'mode': 'courier',
        'ocr': "PUNJAB NATIONAL BANK\nREGIONAL OFFICE, HYDERABAD\n\nRef: PNB/HYD/FD-MAT/2025/0234\nDate: 16.06.2025\n\nSubject: Fixed Deposit Maturity Notification — FD No. 4567891234.\n\nThis is to inform you that your Fixed Deposit of Rs. 25,00,000/- (Twenty-Five Lakhs Only) is maturing on 30.06.2025. Current interest earned: Rs. 1,87,500/-. Please advise whether to renew or close the deposit. If no instructions are received, the amount will be credited to your savings account.",
    },
    {
        'days': 3, 'sender': 'Shri R.N. Prasad, Assistant Director',
        'org': 'Directorate General of Training (DGT), Ministry of Skill Development',
        'addr': 'DGT, Shram Shakti Bhawan, Rafi Marg, New Delhi-110001',
        'subject': 'Skill India Mission — apprenticeship quota compliance for FY 2025-26',
        'dept': 'HR', 'doc_type': 'circular', 'pages': 4, 'status': 'routed',
        'mode': 'speed_post',
        'ocr': "DIRECTORATE GENERAL OF TRAINING\nMINISTRY OF SKILL DEVELOPMENT AND ENTREPRENEURSHIP\n\nCircular No.: DGT/AP/2025-26/QUOTA/0345\nDate: 16.06.2025\n\nSubject: Apprenticeship Quota Compliance under the Apprentices Act, 1961 for FY 2025-26.\n\nAll establishments having workforce above 30 are mandated to engage apprentices between 2.5% to 15% of their total strength. You are directed to register on the NAPS portal and submit your engagement plan by 31.07.2025.",
    },
    {
        'days': 2, 'sender': 'Shri K.V. Rao, Commissioner',
        'org': 'Greater Hyderabad Municipal Corporation (GHMC)',
        'addr': 'GHMC Head Office, Tank Bund Road, Hyderabad-500080',
        'subject': 'Trade license renewal notice for office canteen and guest house operations',
        'dept': 'ADMIN', 'doc_type': 'legal_notice', 'pages': 2, 'status': 'routed',
        'mode': 'hand_delivery',
        'ocr': "GREATER HYDERABAD MUNICIPAL CORPORATION\n\nRef: GHMC/TL/REN/2025/BH-04567\nDate: 17.06.2025\n\nSubject: Trade License Renewal for Office Canteen and Guest House.\n\nYour trade license (No. BH-2023-04567) for operating office canteen and guest house facilities at Plot No. 12, Banjara Hills is expiring on 31.07.2025. Renewal application with FSSAI license, fire NOC, and structural stability certificate must be submitted by 15.07.2025. Renewal fee: Rs. 15,000/-.",
    },
    {
        'days': 2, 'sender': 'The Director, NASSCOM Foundation',
        'org': 'NASSCOM, Cyber Gateway, Hyderabad',
        'addr': 'NASSCOM, Plot No. 7-10, Cyber Gateway, HITEC City, Hyderabad-500081',
        'subject': 'Partnership proposal for digital literacy programme in affiliated rural schools',
        'dept': 'IT', 'doc_type': 'correspondence', 'pages': 5, 'status': 'routed',
        'mode': 'courier',
        'ocr': "NASSCOM FOUNDATION\nHYDERABAD CHAPTER\n\nRef: NASSCOM/HYD/DLP/2025/0089\nDate: 17.06.2025\n\nSubject: Partnership Proposal for Digital Literacy Programme in CISCE Affiliated Rural Schools.\n\nNASSCOM Foundation proposes a CSR-funded digital literacy programme for CISCE affiliated schools in rural Telangana. The programme will provide computer labs, teacher training, and online learning platforms to 50 schools over 2 years. Total project value: Rs. 2.5 Crores (NASSCOM funded). MoU draft enclosed.",
    },

    # ======================================================================
    # GROUP 7 — SCANNED, 1-2 days ago (3 docs)
    # ======================================================================
    {
        'days': 2, 'sender': 'Smt. Malathi Devi, Accounts Officer',
        'org': 'Kendriya Vidyalaya Sangathan (KVS), Hyderabad Region',
        'addr': 'KVS Regional Office, Begumpet, Hyderabad-500016',
        'subject': 'Request for sharing examination evaluation software and technical documentation',
        'dept': 'IT', 'doc_type': 'correspondence', 'pages': 3, 'status': 'scanned',
        'mode': 'speed_post',
        'ocr': "KENDRIYA VIDYALAYA SANGATHAN\nREGIONAL OFFICE, HYDERABAD\n\nRef: KVS/RO-HYD/IT/2025/0456\nDate: 17.06.2025\n\nSubject: Request for Sharing Examination Evaluation Software and Technical Documentation.\n\nKVS Regional Office, Hyderabad seeks your cooperation in sharing the technical specifications and documentation of the digital evaluation software used by CISCE for board examinations. This is for the purpose of developing a similar system for KV internal examinations. A formal MoU can be executed if required.",
    },
    {
        'days': 1, 'sender': 'Shri Govind Rajan, Joint Director',
        'org': 'Directorate of Economics and Statistics, Government of Telangana',
        'addr': 'Directorate of E&S, 5th Floor, BRKR Bhavan, Tank Bund, Hyderabad-500063',
        'subject': 'Annual statistical data requisition for educational indicators — Telangana State Report 2025',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 4, 'status': 'scanned',
        'mode': 'courier',
        'ocr': "DIRECTORATE OF ECONOMICS AND STATISTICS\nGOVERNMENT OF TELANGANA\n\nRef: DES/TS/EDU-STAT/2025/0234\nDate: 18.06.2025\n\nSubject: Annual Statistical Data Requisition for Educational Indicators — Telangana State Report 2025.\n\nYou are requested to furnish the following data for inclusion in the Telangana State Statistical Report 2025:\n1. Number of affiliated schools (district-wise).\n2. Student enrollment figures for ICSE and ISC (last 5 years).\n3. Pass percentage trends.\n4. Gender-wise and category-wise breakup.\n\nData to be submitted in prescribed Format-EDU-7 by 30.07.2025.",
    },
    {
        'days': 1, 'sender': 'The Chief Medical Officer',
        'org': 'Central Government Health Scheme (CGHS), Hyderabad',
        'addr': 'CGHS Wellness Centre, Nampally, Hyderabad-500001',
        'subject': 'Revised CGHS card issuance procedure and annual medical check-up schedule 2025',
        'dept': 'HR', 'doc_type': 'circular', 'pages': 3, 'status': 'scanned',
        'mode': 'hand_delivery',
        'ocr': "CENTRAL GOVERNMENT HEALTH SCHEME\nWELLNESS CENTRE, HYDERABAD\n\nCircular No.: CGHS/HYD/CARD/2025/078\nDate: 18.06.2025\n\nSubject: Revised CGHS Card Issuance Procedure and Annual Medical Check-up Schedule 2025.\n\nAll government employees and pensioners are informed that CGHS cards will now be issued in Aadhaar-linked digital format through the CGHS portal. Annual medical check-up camps will be conducted in July 2025 at all CGHS wellness centres. Employees are requested to register online.",
    },

    # ======================================================================
    # GROUP 8 — RECEIVED, today (2 docs)
    # ======================================================================
    {
        'days': 0, 'sender': 'Shri Mohan Lal Gupta, Commissioner',
        'org': 'Central Bureau of Investigation (CBI), Hyderabad Branch',
        'addr': 'CBI, 5-9-60, Chapel Road, Nampally, Hyderabad-500001',
        'subject': 'Request for certified copies of financial records pertaining to Case RC/HYD/2025/E/0023',
        'dept': 'FINAC', 'doc_type': 'legal_notice', 'pages': 2, 'status': 'received',
        'mode': 'hand_delivery',
        'ocr': None,
    },
    {
        'days': 0, 'sender': 'Dr. Prashant Mehta, Director',
        'org': 'National Council of Educational Research and Training (NCERT)',
        'addr': 'NCERT, Sri Aurobindo Marg, New Delhi-110016',
        'subject': 'Invitation to participate in National Curriculum Framework review workshop — July 2025',
        'dept': 'ADMIN', 'doc_type': 'correspondence', 'pages': 4, 'status': 'received',
        'mode': 'speed_post',
        'ocr': None,
    },
]

# ---------------------------------------------------------------------------
# Main seeder
# ---------------------------------------------------------------------------

def seed_mock_data():
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("  DocTrack — Comprehensive Mock Data Seeder")
        print("=" * 60)
        print()

        # ── Wipe existing data ──
        print("[1/6] Dropping and recreating all tables …")
        db.drop_all()
        db.create_all()

        # ── Departments ──
        print("[2/6] Creating 6 departments …")
        dept_map = {}  # code -> Department
        for d in DEPARTMENTS:
            dept = Department(
                department_name=d['name'],
                department_code=d['code'],
            )
            db.session.add(dept)
            db.session.flush()
            dept_map[d['code']] = dept
        db.session.commit()

        # ── Users ──
        print("[3/6] Creating 16 users …")
        pw_hash = hash_pw('Admin@123')  # same password for all
        user_map = {}   # username -> User
        heads = {}      # dept_code -> user_id (for heads)

        for u in USERS:
            dept_id = None
            if u.get('dept_code'):
                dept_id = dept_map[u['dept_code']].department_id
            user = User(
                username=u['username'],
                password_hash=pw_hash,
                full_name=u['full_name'],
                email=u['email'],
                role=u['role'],
                department_id=dept_id,
                is_active=True,
                last_login=datetime.utcnow() - timedelta(
                    hours=random.randint(1, 72)
                ) if u['role'] != 'superadmin' else None,
            )
            db.session.add(user)
            db.session.flush()
            user_map[u['username']] = user
            if u.get('is_head'):
                heads[u['dept_code']] = user.user_id
        db.session.commit()

        # Set department heads
        for code, uid in heads.items():
            dept_map[code].head_user_id = uid
        db.session.commit()

        # Helper lookups
        receptionists = [user_map['reception1'], user_map['reception2']]

        def dept_users_for(code):
            """Return list of dept_user User objects for a department code."""
            return [u for u in user_map.values()
                    if u.department and u.department.department_code == code
                    and u.role == 'dept_user']

        admins = [u for u in user_map.values() if u.role in ('admin', 'superadmin')]

        # ── Documents ──
        print("[4/6] Creating 60 documents with full lifecycle records …")
        status_counts = {}
        now = datetime.utcnow()
        sla_hours = app.config.get('SLA_HOURS', 48)

        for idx, d in enumerate(DOCS, start=1):
            tracking_id = f"DOC-2025-{str(idx).zfill(5)}"
            days_ago = d['days']
            recv_date = (now - timedelta(days=days_ago)).date()
            recv_time = rand_time()
            recv_dt = datetime.combine(recv_date, recv_time)
            receptionist = random.choice(receptionists)

            ocr_status = 'completed'
            if d['status'] == 'received':
                ocr_status = 'pending'

            doc = Document(
                tracking_id=tracking_id,
                date_received=recv_date,
                time_received=recv_time,
                mode_of_receipt=d.get('mode', rand_mode()),
                sender_name=d['sender'],
                sender_organisation=d['org'],
                sender_address=d.get('addr'),
                subject_description=d['subject'],
                number_of_pages=d.get('pages', random.randint(2, 10)),
                file_path=None,
                file_type=None,
                ocr_text=d.get('ocr'),
                ocr_status=ocr_status,
                status=d['status'],
                created_by=receptionist.user_id,
                created_at=recv_dt,
                updated_at=recv_dt,
            )
            db.session.add(doc)
            db.session.flush()

            status_counts[d['status']] = status_counts.get(d['status'], 0) + 1

            # ── Tracking Events chain ──
            event_time = recv_dt + timedelta(minutes=random.randint(1, 5))

            # REGISTERED
            db.session.add(TrackingEvent(
                document_id=doc.document_id,
                event_type='REGISTERED',
                event_description=f'Document registered by {receptionist.full_name}',
                performed_by=receptionist.user_id,
                performed_at=event_time,
            ))

            # Audit log for registration
            db.session.add(AuditLog(
                event_type='DOCUMENT_REGISTERED',
                document_id=doc.document_id,
                user_id=receptionist.user_id,
                ip_address='192.168.1.' + str(random.randint(10, 250)),
                details=f'Document {tracking_id} registered',
                logged_at=event_time,
            ))

            if d['status'] == 'received':
                continue  # No further processing

            # OCR COMPLETED
            event_time += timedelta(minutes=random.randint(2, 10))
            db.session.add(TrackingEvent(
                document_id=doc.document_id,
                event_type='OCR_COMPLETED',
                event_description='OCR text extraction completed successfully',
                performed_by=None,
                performed_at=event_time,
            ))

            if d['status'] == 'scanned':
                continue  # Stop here

            # CATEGORISED
            dept_code = d['dept']
            dept_obj = dept_map[dept_code]
            target_users = dept_users_for(dept_code)
            target_user = random.choice(target_users) if target_users else list(user_map.values())[4]
            confidence = round(random.uniform(0.78, 0.97), 3)

            event_time += timedelta(minutes=random.randint(1, 3))
            cat = Categorisation(
                document_id=doc.document_id,
                suggested_department_id=dept_obj.department_id,
                suggested_user_id=target_user.user_id,
                document_type=d['doc_type'],
                confidence_score=confidence,
                method='ai_auto',
                categorised_by=receptionist.user_id,
                categorised_at=event_time,
            )
            db.session.add(cat)

            db.session.add(TrackingEvent(
                document_id=doc.document_id,
                event_type='CATEGORISED',
                event_description=(
                    f'AI categorised as {d["doc_type"].replace("_"," ").title()} '
                    f'for {dept_obj.department_name} (confidence: {confidence:.1%})'
                ),
                performed_by=None,
                performed_at=event_time,
            ))

            if d['status'] == 'categorised':
                continue

            # ROUTED
            event_time += timedelta(minutes=random.randint(5, 30))
            route_dt = event_time
            sla_deadline = route_dt + timedelta(hours=sla_hours)

            routing = Routing(
                document_id=doc.document_id,
                routed_to_department_id=dept_obj.department_id,
                routed_to_user_id=target_user.user_id,
                routed_by=receptionist.user_id,
                routed_at=route_dt,
                sla_deadline=sla_deadline,
            )
            db.session.add(routing)

            db.session.add(TrackingEvent(
                document_id=doc.document_id,
                event_type='ROUTED',
                event_description=(
                    f'Routed to {target_user.full_name} '
                    f'({dept_obj.department_name}), SLA: '
                    f'{sla_deadline.strftime("%d-%b-%Y %H:%M")}'
                ),
                performed_by=receptionist.user_id,
                performed_at=route_dt,
            ))

            db.session.add(AuditLog(
                event_type='DOCUMENT_ROUTED',
                document_id=doc.document_id,
                user_id=receptionist.user_id,
                ip_address='192.168.1.' + str(random.randint(10, 250)),
                details=(
                    f'{tracking_id} routed to {target_user.full_name} '
                    f'({dept_obj.department_code})'
                ),
                logged_at=route_dt,
            ))

            if d['status'] == 'routed':
                continue

            # NOTIFIED
            event_time += timedelta(minutes=random.randint(1, 5))
            db.session.add(TrackingEvent(
                document_id=doc.document_id,
                event_type='NOTIFIED',
                event_description=f'Notification sent to {target_user.full_name}',
                performed_by=None,
                performed_at=event_time,
            ))

            db.session.add(Notification(
                document_id=doc.document_id,
                user_id=target_user.user_id,
                notification_type='new_document',
                message=(
                    f'New document {tracking_id}: '
                    f'"{d["subject"][:80]}…" has been assigned to you.'
                ),
                is_read=(d['status'] not in ('notified',)),
                created_at=event_time,
                read_at=event_time + timedelta(hours=random.randint(1, 12))
                if d['status'] not in ('notified',) else None,
            ))

            if d['status'] == 'notified':
                continue

            # ESCALATED
            if d['status'] == 'escalated':
                esc_time = sla_deadline + timedelta(hours=random.randint(1, 12))
                db.session.add(TrackingEvent(
                    document_id=doc.document_id,
                    event_type='ESCALATED',
                    event_description=(
                        f'Document escalated: SLA deadline '
                        f'({sla_deadline.strftime("%d-%b-%Y %H:%M")}) breached'
                    ),
                    performed_by=None,
                    performed_at=esc_time,
                ))

                # Escalation notifications
                for admin_user in admins:
                    db.session.add(Notification(
                        document_id=doc.document_id,
                        user_id=admin_user.user_id,
                        notification_type='escalation',
                        message=(
                            f'ESCALATION: {tracking_id} '
                            f'"{d["subject"][:60]}…" SLA breached'
                        ),
                        is_read=False,
                        created_at=esc_time,
                    ))
                # Notify dept head
                head_uid = heads.get(dept_code)
                if head_uid:
                    db.session.add(Notification(
                        document_id=doc.document_id,
                        user_id=head_uid,
                        notification_type='escalation',
                        message=(
                            f'ESCALATION: {tracking_id} in your department '
                            f'has breached SLA deadline'
                        ),
                        is_read=False,
                        created_at=esc_time,
                    ))
                continue

            # ACKNOWLEDGED
            if d['status'] in ('acknowledged', 'archived'):
                ack_time = event_time + timedelta(
                    hours=random.randint(2, int(sla_hours * 0.8))
                )
                remark = random.choice(ACK_REMARKS)
                was_esc = False

                ack = Acknowledgement(
                    document_id=doc.document_id,
                    acknowledged_by=target_user.user_id,
                    acknowledged_at=ack_time,
                    remarks=remark,
                    was_escalated=was_esc,
                )
                db.session.add(ack)

                db.session.add(TrackingEvent(
                    document_id=doc.document_id,
                    event_type='ACKNOWLEDGED',
                    event_description=(
                        f'Acknowledged by {target_user.full_name}: "{remark}"'
                    ),
                    performed_by=target_user.user_id,
                    performed_at=ack_time,
                ))

                # Ack notification to receptionist
                db.session.add(Notification(
                    document_id=doc.document_id,
                    user_id=receptionist.user_id,
                    notification_type='acknowledgement_done',
                    message=(
                        f'{tracking_id} acknowledged by '
                        f'{target_user.full_name}'
                    ),
                    is_read=True,
                    created_at=ack_time,
                    read_at=ack_time + timedelta(hours=random.randint(1, 8)),
                ))

                db.session.add(AuditLog(
                    event_type='ACKNOWLEDGED',
                    document_id=doc.document_id,
                    user_id=target_user.user_id,
                    ip_address='192.168.1.' + str(random.randint(10, 250)),
                    details=f'{tracking_id} acknowledged: {remark}',
                    logged_at=ack_time,
                ))

                # ARCHIVED (additional step)
                if d['status'] == 'archived':
                    arch_time = ack_time + timedelta(days=random.randint(3, 10))
                    db.session.add(TrackingEvent(
                        document_id=doc.document_id,
                        event_type='ARCHIVED',
                        event_description='Document archived after processing',
                        performed_by=admins[0].user_id,
                        performed_at=arch_time,
                    ))
                    db.session.add(AuditLog(
                        event_type='DOCUMENT_ARCHIVED',
                        document_id=doc.document_id,
                        user_id=admins[0].user_id,
                        ip_address='192.168.1.100',
                        details=f'{tracking_id} archived',
                        logged_at=arch_time,
                    ))

        db.session.commit()

        # ── Login audit logs for realism ──
        print("[5/6] Creating login/logout audit entries …")
        for user in user_map.values():
            if user.role == 'superadmin':
                continue
            for day_offset in range(0, 60, random.randint(1, 4)):
                login_time = now - timedelta(
                    days=day_offset,
                    hours=random.randint(0, 3),
                )
                db.session.add(AuditLog(
                    event_type='LOGIN',
                    user_id=user.user_id,
                    ip_address='192.168.1.' + str(random.randint(10, 250)),
                    details=f'{user.full_name} logged in',
                    logged_at=login_time,
                ))
                db.session.add(AuditLog(
                    event_type='LOGOUT',
                    user_id=user.user_id,
                    ip_address='192.168.1.' + str(random.randint(10, 250)),
                    details=f'{user.full_name} logged out',
                    logged_at=login_time + timedelta(
                        hours=random.randint(1, 8)
                    ),
                ))
        db.session.commit()

        # ── Summary ──
        print("[6/6] Done!")
        print()
        print("=" * 60)
        print("  SEEDING COMPLETE — SUMMARY")
        print("=" * 60)
        print()
        print(f"  Departments created:  {len(DEPARTMENTS)}")
        print(f"  Users created:        {len(USERS)}")
        print(f"  Documents created:    {len(DOCS)}")
        print()
        print("  Documents by Status:")
        for status in ['received', 'scanned', 'categorised', 'routed',
                       'notified', 'acknowledged', 'escalated', 'archived']:
            count = status_counts.get(status, 0)
            if count:
                print(f"    {status.upper():20s}  {count:3d}")
        print()
        total_events = TrackingEvent.query.count()
        total_notifs = Notification.query.count()
        total_audits = AuditLog.query.count()
        print(f"  Tracking events:      {total_events}")
        print(f"  Notifications:        {total_notifs}")
        print(f"  Audit log entries:    {total_audits}")
        print()
        print("=" * 60)
        print("  LOGIN CREDENTIALS (all passwords: Admin@123)")
        print("=" * 60)
        print(f"  {'Role':<20s} {'Username':<16s} {'Full Name':<30s}")
        print(f"  {'-'*20} {'-'*16} {'-'*30}")
        for u in USERS:
            role_display = u['role'].replace('_', ' ').title()
            if u.get('dept_code'):
                role_display = f"Dept ({u['dept_code']})"
            print(f"  {role_display:<20s} {u['username']:<16s} {u['full_name']:<30s}")
        print()
        print("  Open http://localhost:5000 and login to explore!")
        print("=" * 60)


if __name__ == '__main__':
    seed_mock_data()
