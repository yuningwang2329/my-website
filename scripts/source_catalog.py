"""Stable journal-source catalog for the mathematical-fluid paper tracker."""

from urllib.parse import urlencode


GROUP_IDS = (
    "math-fluid-pde",
    "top-general-math",
    "high-general-math",
)


FEEDS = [
    {
        "name": "Arxiv (math.AP)",
        "url": "http://export.arxiv.org/api/query?search_query=cat:math.AP&sortBy=submittedDate&sortOrder=descending&max_results=50",
        "type": "arxiv",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Appl. Math. Lett.",
        "url": "https://rss.sciencedirect.com/publication/science/08939659",
        "type": "standard_rss",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Arch. Ration. Mech. Anal.",
        "url": "1432-0673",
        "type": "crossref_journal",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Commun. Math. Phys.",
        "url": "1432-0916",
        "type": "crossref_journal",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Commun. Pure Appl. Math.",
        "url": "https://onlinelibrary.wiley.com/action/showFeed?type=etoc&feed=rss&jc=10970312",
        "type": "standard_rss",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Calc. Var. Partial Differ. Equ.",
        "url": "1432-0835",
        "type": "crossref_journal",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "J. Differ. Equ.",
        "url": "https://rss.sciencedirect.com/publication/science/00220396",
        "type": "standard_rss",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "J. Funct. Anal.",
        "url": "https://rss.sciencedirect.com/publication/science/00221236",
        "type": "standard_rss",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "SIAM J. Math. Anal.",
        "url": "https://epubs.siam.org/action/showFeed?type=etoc&feed=rss&jc=sjmaah",
        "type": "standard_rss",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "J. Math. Pures Appl.",
        "url": "https://rss.sciencedirect.com/publication/science/00217824",
        "type": "standard_rss",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "J. Math. Fluid Mech.",
        "url": "1422-6952",
        "type": "crossref_journal",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Ann. Inst. H. Poincaré C Anal. Non Linéaire",
        "url": "1873-1430",
        "type": "crossref_journal",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Analysis & PDE",
        "url": "1948-206X",
        "type": "crossref_journal",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Nonlinearity",
        "url": "1361-6544",
        "type": "crossref_journal",
        "source_group": "math-fluid-pde",
    },
    {
        "name": "Ann. of Math.",
        "url": "0003-486X",
        "type": "crossref_journal",
        "source_group": "top-general-math",
    },
    {
        "name": "Acta Math.",
        "url": "1871-2509",
        "type": "crossref_journal",
        "source_group": "top-general-math",
    },
    {
        "name": "Invent. Math.",
        "url": "1432-1297",
        "type": "crossref_journal",
        "source_group": "top-general-math",
    },
    {
        "name": "J. Amer. Math. Soc.",
        "url": "1088-6834",
        "type": "crossref_journal",
        "source_group": "top-general-math",
    },
    {
        "name": "Publ. Math. IHÉS",
        "url": "1618-1913",
        "type": "crossref_journal",
        "source_group": "top-general-math",
    },
    {
        "name": "Proc. Lond. Math. Soc.",
        "url": "https://londmathsoc.onlinelibrary.wiley.com/feed/1460244x/most-recent",
        "type": "standard_rss",
        "source_group": "high-general-math",
    },
    {
        "name": "J. Lond. Math. Soc.",
        "url": "https://londmathsoc.onlinelibrary.wiley.com/feed/14697750/most-recent",
        "type": "standard_rss",
        "source_group": "high-general-math",
    },
    {
        "name": "Duke Math. J.",
        "url": "1547-7398",
        "type": "crossref_journal",
        "source_group": "high-general-math",
    },
    {
        "name": "J. Eur. Math. Soc.",
        "url": "1435-9863",
        "type": "crossref_journal",
        "source_group": "high-general-math",
    },
    {
        "name": "Ann. Sci. Éc. Norm. Supér.",
        "url": "1873-2151",
        "type": "crossref_journal",
        "source_group": "high-general-math",
    },
    {
        "name": "Adv. Math.",
        "url": "https://rss.sciencedirect.com/publication/science/00018708",
        "type": "standard_rss",
        "source_group": "high-general-math",
    },
    {
        "name": "J. Reine Angew. Math.",
        "url": "1435-5345",
        "type": "crossref_journal",
        "source_group": "high-general-math",
    },
    {
        "name": "Selecta Math.",
        "url": "1420-9020",
        "type": "crossref_journal",
        "source_group": "high-general-math",
    },
    {
        "name": "Forum Math. Pi",
        "url": "2050-5086",
        "type": "crossref_journal",
        "source_group": "high-general-math",
    },
]


SOURCE_GROUP_BY_NAME = {feed["name"]: feed["source_group"] for feed in FEEDS}

FALLBACK_KEYWORDS = (
    "fluid",
    "navier-stokes",
    "navier stokes",
    "euler equation",
    "hydrodynamic",
    "mhd",
    "magnetohydrodynamic",
    "boussinesq",
    "water wave",
    "boundary layer",
    "compressible flow",
    "incompressible",
    "vortex",
    "vorticity",
    "viscous flow",
    "inviscid flow",
    "burgers equation",
    "korteweg",
    "stokes equation",
    "stokes system",
    "capillary",
    "convection",
    "turbulence",
    "shallow water",
    "couette",
    "thin-film",
    "thin film",
    "hele-shaw",
    "dongyi wei",
    "camassa",
    "fluid-structure",
    "non-newtonian",
    "non newtonian",
    "viscoelastic",
    "multiphase",
    "two-phase",
    "two phase",
    "porous media",
)

EXCLUDE_KEYWORDS = (
    "quantum information",
    "algebraic geometry",
    "general relativity",
    "number theory",
    "riemannian",
    "groupoid",
    "k-theory",
    "biofilm",
    "ecology",
    "epidem",
    "sir model",
    "machine learning",
    "neural network",
    "deep learning",
    "stochastic gradient",
    "tensor pca",
)


def build_crossref_works_url(issn, rows=15):
    """Build a Crossref query that excludes issue-level metadata records."""
    query = urlencode(
        {
            "filter": "type:journal-article",
            "sort": "published",
            "order": "desc",
            "rows": rows,
        }
    )
    return f"https://api.crossref.org/journals/{issn}/works?{query}"


def source_group_for_source(source):
    """Return the stable journal group for a displayed source name, if known."""
    return SOURCE_GROUP_BY_NAME.get(source)


def matches_fluid_fallback(title, abstract):
    """Classify obvious mathematical-fluid papers when the LLM is unavailable."""
    text = f"{title} {abstract}".lower()
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return False
    return any(word in text for word in FALLBACK_KEYWORDS)
