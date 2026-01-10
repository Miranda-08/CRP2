from pathlib import Path
from owlready2 import get_ontology, onto_path

from ontology.build_ontology import build_ontology
from ontology.data_seed import seed_demo_data
from ontology.reasoning import refresh_inferences
from ui.cli import run_cli

ONTO_IRI = "http://example.org/room_mgmt.owl"
OWL_FILENAME = "room_mgmt.owl"


def load_or_create_ontology(project_dir: Path):
    owl_file = project_dir / OWL_FILENAME

    # Ensure owlready2 searches this directory for local ontologies
    dir_str = str(project_dir)
    if dir_str not in onto_path:
        onto_path.append(dir_str)

    if owl_file.exists():
        onto = get_ontology(str(owl_file)).load()
        print(f"Loaded ontology from {owl_file}")
        return onto, False

    # Create new ontology (logical IRI)
    onto = get_ontology(ONTO_IRI)

    # Build schema (classes + properties) - must NOT save here
    build_ontology(onto)

    # Seed demo data
    seed_demo_data(onto)

    # Initial inference refresh
    refresh_inferences(onto)

    # Save once, here
    onto.save(file=str(owl_file), format="rdfxml")
    print(f"Created and saved new ontology to {owl_file}")

    return onto, True


def main():
    project_dir = Path(__file__).resolve().parent
    owl_file = project_dir / OWL_FILENAME

    onto, created_new = load_or_create_ontology(project_dir)

    # Keep inferred classes consistent every run
    refresh_inferences(onto)

    # Run console UI
    run_cli(onto)

    # Persist changes (e.g., new bookings)
    onto.save(file=str(owl_file), format="rdfxml")
    print(f"Saved ontology to {owl_file}")


if __name__ == "__main__":
    main()
