import re


CLUBS = [
    ("JUIT Youth Club (JYC)", "https://www.juit.ac.in/juit-youth-club"),
    ("National Service Scheme (NSS)", "https://www.juit.ac.in/nss-in-juit"),
    ("National Cadet Corps (NCC)", "https://www.juit.ac.in/ncc"),
    ("Civil Engineering Consortium (CEC)", "https://www.juit.ac.in/civil-engineering-cec"),
    ("Coding Society JUIT", "https://www.juit.ac.in/coding-society-juit-cse-it"),
    ("IEEE JUIT Student Branch", "https://www.juit.ac.in/ieee-student-branch"),
    ("JUIT Synapse", "https://www.juit.ac.in/synapse-students-club"),
    ("Technical Club ENKINDLE", "https://www.juit.ac.in/technical-club-cse-it"),
    ("Technovatorz: Electronics Club", "https://www.juit.ac.in/technovatorz-electronics-club"),
    ("Koshish Club", "https://www.juit.ac.in/koshishclub"),
    ("Gender Champions Club", "https://www.juit.ac.in/gender-champions-club"),
]

RESEARCH_CENTERS = [
    (
        "Centre for Structural Engineering and Disaster Management (CESEDM)",
        "https://www.juit.ac.in/Centre-of-Excellence-in-Structural-Engineering-and-Disaster-Management",
    ),
    (
        "Centre of Sustainable Technologies for Rural Development (CESTRD)",
        "https://www.juit.ac.in/biotechnology-bioinformatics-cestrd",
    ),
    (
        "Centre for Climate Change and Water Resources (CCCWR)",
        "https://www.juit.ac.in/Centre-for-Climate-Change-and-Water-Resources",
    ),
    (
        "Centre of Healthcare Technologies and Informatics (CEHTI)",
        "https://www.juit.ac.in/biotechnology-bioinformatics-cehti",
    ),
    (
        "Center of Excellence - Industry 5.0",
        "https://www.juit.ac.in/center-of-excellence-Industry",
    ),
    (
        "Center of Excellence LDRA",
        "https://www.juit.ac.in/center-of-excellence-ldra-cse-it",
    ),
    (
        "Centre of Excellence for Intelligent Evaluation and Rehabilitation of Structures",
        "https://www.juit.ac.in/RIDE-centre-of-excellence",
    ),
]

COMMITTEES = [
    "Committee for Assessment & Disposal of Expired Chemicals/Reagents",
    "University Committee for Prevention of Unfair Means",
    "Anti Ragging Committee (2025-26)",
    "Committee for R&D Cell",
    "Equal Opportunity Committee",
    "Sub Committee of Academic Council",
    "TOFEI Guidelines / NHM Shimla / JUIT Waknaghat Committee",
    "Committee for B.Sc. in Forensic Science (Dept. of BT&BI)",
    "Internal Complaint Committee (ICC)",
    "Grievance Redressal Committee for Employees",
    "Committee for Internationalization of Higher Education in JUIT",
    "Disciplinary Committee",
    "Anti Drug Committee of JUIT",
    "Student Counselling Committee 2025-26",
    "Nasha Mukt Hostel Committee 2025",
    "NBA Committee - BTech CSE",
    "Sambhavna Samvad Samadhan",
    "JYC Faculty Coordinators 2025-26",
    "JUIT Library Committee",
    "Anti Ragging Sub Committee",
    "Anti Ragging Squad",
    "Research Advisory & Project Monitoring Committee",
    "UGC Task Groups",
    "TIEDC Committee",
    "Training & Development Cell (Including Industry Interaction)",
    "VIKSIT BHARAT@2047",
    "NBA Committee",
    "MOODLE Committee of JUIT",
    "Faculty Advisory Board",
    "ISO Certification of the University",
    "E-Governance Committee for JUIT",
    "Committee for Publicity Through Media for Attracting Admissions",
    "Committee for G-Suite Implementation in JUIT",
    "Dept Faculty Coordinator for Alumni Affairs",
    "Academic Support Programme for SC Students",
    "Committee for care of day to day needs of differently abled persons and implementation of schemes",
    "JYC Student Office Bearers & Coordinators 2024-2025",
    "Student Grievance Redressal Committee (SGRC)",
    "Scholarships Committee",
    "Ethics Committee",
    "Hostel Advisory Committee (2024 - 2025)",
    "Admission Screening Committee for MSc DBT Supported Program 2023-25",
    "Divyangjan Policy & Initiatives",
    "NEP Committees",
    "Anti Discrimination Officer",
    "Standing Enquiry Committee & FIR Committee",
    "Council of Institution-Industry Linkages",
    "Committee for Complaints against Caste Based Discrimination",
    "Time Table Committee",
    "Website Committee",
]


def _format_names(items):
    return "; ".join(name for name, _url in items)


def club_answer():
    return (
        "Student clubs and student organizations at JUIT include: "
        f"{_format_names(CLUBS)}."
    )


def research_center_answer():
    return (
        "Research centers and centers of excellence at JUIT include: "
        f"{_format_names(RESEARCH_CENTERS)}."
    )


def committee_answer():
    return "The JUIT committees page lists: " + "; ".join(COMMITTEES) + "."


def placement_answer(documents):
    for document in documents:
        ce_answer = _civil_engineering_placement_answer(document)

        if ce_answer:
            return ce_answer

    for document in documents:
        stats_answer = _latest_civil_placement_statistics_answer(document)

        if stats_answer:
            return stats_answer

    return None


def _civil_engineering_placement_answer(document):
    match = re.search(
        r"Batch\s+((?:\d{4}-\d{4}\s+)+)No\. of Eligible Students\s+"
        r"((?:\d+\s+)+)No\. of Students Placed\s+((?:\d+\s*)+)",
        document,
    )

    if not match:
        return None

    batches = match.group(1).split()
    eligible = [int(value) for value in match.group(2).split()]
    placed = [int(value) for value in match.group(3).split()]

    rows = [
        f"{batch}: {placed_count} placed out of {eligible_count} eligible"
        for batch, eligible_count, placed_count in zip(batches, eligible, placed)
    ]

    return (
        "Civil Engineering placement statistics from the CE placements page are: "
        + "; ".join(rows)
        + "."
    )


def _latest_civil_placement_statistics_answer(document):
    match = re.search(
        r"PLACEMENT STATUS : JUIT, SOLAN (?P<batch>\d{4}-\d{2}).*?"
        r"CIVIL\s+(?P<eligible>\d+)\s+(?P<absolute>\d+)\s+"
        r"(?P<absolute_percent>\d+%)\s+(?P<offers>\d+)\s+(?P<offers_percent>\d+%)",
        document,
    )

    if not match:
        return None

    return (
        f"For Civil Engineering in placement batch {match.group('batch')}, "
        f"{match.group('eligible')} students were eligible/participating, "
        f"{match.group('absolute')} absolute offers were recorded "
        f"({match.group('absolute_percent')}), and {match.group('offers')} total offers "
        f"were recorded ({match.group('offers_percent')})."
    )
