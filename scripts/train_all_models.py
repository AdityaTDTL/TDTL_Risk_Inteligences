from tdtl_risk_ai.pipelines.training_pipeline import train_all

if __name__ == "__main__":
    outputs = train_all()
    print("Saved model artifacts:")
    for k, v in outputs.items():
        print(f"- {k}: {v}")
