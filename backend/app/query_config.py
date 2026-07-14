from dataclasses import dataclass


@dataclass(frozen=True)
class EntityAlias:
    canonical: str
    aliases: tuple[str, ...]


ROLE_ALIASES: tuple[EntityAlias, ...] = (
    EntityAlias("Vice Chancellor", ("vc", "vice chancellor", "vice-chancellor")),
    EntityAlias("Head of Department", ("hod", "head of department", "head of dept")),
    EntityAlias("Registrar", ("registrar",)),
    EntityAlias("Dean", ("dean",)),
    EntityAlias("Chancellor", ("chancellor",)),
)

DEPARTMENT_ALIASES: tuple[EntityAlias, ...] = (
    EntityAlias(
        "Computer Science Engineering and Information Technology",
        (
            "cse",
            "cse it",
            "cse-it",
            "computer science",
            "computer science engineering",
            "information technology",
            "computer science engineering information technology",
        ),
    ),
    EntityAlias(
        "Electronics and Communication Engineering",
        (
            "ece",
            "ecs",
            "electronics",
            "electronics communication",
            "electronics and communication",
            "electronics and communication engineering",
        ),
    ),
    EntityAlias(
        "Civil Engineering",
        ("ce", "civil", "civil engineering"),
    ),
    EntityAlias(
        "Biotechnology and Bioinformatics",
        (
            "bt",
            "bi",
            "bi bt",
            "bt bi",
            "biotechnology",
            "bioinformatics",
            "biotechnology and bioinformatics",
        ),
    ),
    EntityAlias("Mathematics", ("maths", "mathematics")),
    EntityAlias(
        "Physics and Materials Science",
        ("pms", "physics", "materials science", "physics and materials science"),
    ),
    EntityAlias(
        "Humanities and Social Sciences",
        ("hss", "humanities", "social sciences", "humanities and social sciences"),
    ),
)

PROGRAM_ALIASES: tuple[EntityAlias, ...] = (
    EntityAlias("B.Tech", ("btech", "b tech", "b.tech", "bachelor of technology")),
    EntityAlias("M.Tech", ("mtech", "m tech", "m.tech", "master of technology")),
    EntityAlias("Ph.D", ("phd", "ph.d", "doctoral", "doctorate")),
    EntityAlias("MBA", ("mba",)),
    EntityAlias("BBA", ("bba",)),
    EntityAlias("BCA", ("bca",)),
)

GENERAL_ALIASES: tuple[EntityAlias, ...] = (
    EntityAlias("Admission", ("admissions", "admission")),
    EntityAlias("Fee", ("fees", "fee", "fee structure", "fee details")),
    EntityAlias("Hostel", ("hostels", "hostel")),
    EntityAlias("Scholarship", ("scholarships", "scholarship")),
    EntityAlias("Placement", ("placements", "placement", "training and placement", "tnp")),
    EntityAlias("Laboratory", ("labs", "lab", "laboratories", "laboratory")),
)
