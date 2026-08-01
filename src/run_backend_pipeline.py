from src.data_generator import save_login_data
from src.data_validation import main as validate_data
from src.data_preprocessing import preprocess_data
from src.risk_engine import main as run_risk_engine
from src.risk_analysis import main as run_risk_analysis
from src.model_training import main as train_models
from src.auth_optimizer import save_scenario_results


def main():
    """
    Run the complete backend pipeline for the Smart Security Optimizer.
    """

    print("RUNNING COMPLETE BACKEND PIPELINE")
    print("=" * 60)

    print("\n1. Generating synthetic login data...")
    save_login_data()

    print("\n2. Validating data...")
    validate_data()

    print("\n3. Preprocessing data...")
    preprocess_data()

    print("\n4. Applying risk engine...")
    run_risk_engine()

    print("\n5. Running risk analysis...")
    run_risk_analysis()

    print("\n6. Training machine-learning models...")
    train_models()

    print("\n7. Saving authentication optimization scenarios...")
    save_scenario_results()

    print("\nBACKEND PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()