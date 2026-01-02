from ontology.build_ontology import build_ontology
from ontology.data_seed import seed_demo_data
from ontology.reasoning import refresh_inferences
from ui.cli import run_cli

def main():
    onto = build_ontology("room_mgmt.owl")
    onto = seed_demo_data(onto)
    refresh_inferences(onto)
    run_cli(onto)
    onto.save(file="room_mgmt.owl", format="rdfxml")
    print("Saved ontology to room_mgmt.owl")

if __name__ == "__main__":
    main()