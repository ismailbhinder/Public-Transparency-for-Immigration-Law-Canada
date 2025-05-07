import pandas as pd
import re
import os
import argparse
from datasets import load_dataset

# Regular expressions
RE_exclude_refugee = re.compile(
    r'\b(convention refugees?|persons? in need of protection|refugee claimants?|protected persons?)\b',
    re.IGNORECASE
)

RE_patterns = {
    'security': re.compile(
        r'\b(espionages?|against canada|canada[’\'‘`s]* interests?|subversions?|democratic governments?|terrorisms?|dangers? to security|violences?|endangerments?|memberships?|complicity|reasonable grounds? to believe)\b',
        re.IGNORECASE
    ),
    'human_rights': re.compile(
        r'\b(human rights?|international rights?|violations?|senior officials?|governments?|regimes?|genocides?|war crimes?|crimes? against humanity|participations?|contributions?|reasonable grounds? to believe|terrorisms?)\b',
        re.IGNORECASE
    ),
    'serious_criminality': re.compile(
        r'\b(criminal convictions?|foreign convictions?|imprisonments?|10 years|ten years|sentences?|over (6|six) months|serious indictable offences?|commissions?|reasonable grounds? to believe)\b',
        re.IGNORECASE
    ),
    'criminality': re.compile(
        r'\b(criminal convictions?|foreign convictions?|indictments?|indictable offences?|summary offences?|commissions?)\b',
        re.IGNORECASE
    ),
    'organized_criminality': re.compile(
        r'\b(memberships?|criminal activities?|organized crimes?|acting in concert|people smuggling|traffickings?|money launderings?|proceeds? of crime|reasonable grounds? to believe)\b',
        re.IGNORECASE
    ),
    'health_grounds': re.compile(
        r'\b(dangers? to public health|dangers? to public safety|excessive demands? on health services|excessive demands? on social services)\b',
        re.IGNORECASE
    ),
    'financial_reasons': re.compile(
        r'\b(unable or unwilling to support (oneself|dependents?)|arrangements? for care and support|social assistances?)\b',
        re.IGNORECASE
    ),
    'misrepresentation': re.compile(
        r'\b(misrepresenting|withholding|material facts?|errors? in administration|non-disclosures?|omissions?|false statements?|false information)\b',
        re.IGNORECASE
    ),
    'non_compliance': re.compile(
        r'\b(contraventions?|non-compliances?|failures? to comply)\b',
        re.IGNORECASE
    ),
    'inadmissible_family': re.compile(
        r'\b(inadmissible family members?|accompanying family members?)\b',
        re.IGNORECASE
    )
}

def categorize_document_multi(text: str) -> list:
    """
    Categorizes the input legal text into one or more inadmissibility reasons.

    Parameters
    ----------
    text : str
        The legal document text to be analyzed.

    Returns
    -------
    list
        A list of matched inadmissibility categories.
    """
    if re.search(RE_exclude_refugee, text):
        return ['refugee']

    matched = [k for k, v in RE_patterns.items() if re.search(v, text)]
    return matched if matched else ['other']


def process_dataset(dataset_name: str, output_dir: str):
    """
    Loads and processes the specified dataset, saves the output CSV.

    Parameters
    ----------
    dataset_name : str
        The name of the sub-dataset (e.g., "FC", "RAD").

    output_dir : str
        Directory to save the processed CSV file.
    """
    dataset = load_dataset("refugee-law-lab/canadian-legal-data", dataset_name, split="train")
    df = dataset.to_pandas()
    df = df[df['unofficial_text'].str.contains('Minister of Citizenship and Immigration', case=False, na=False)]
    df['inadmissibility_reason'] = df['unofficial_text'].apply(categorize_document_multi)
    final_df = df[['citation', 'dataset', 'year', 'language', 'document_date', 'source_url', 'unofficial_text', 'inadmissibility_reason']]

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{dataset_name}_data.csv")
    final_df.to_csv(file_path, index=False)
    print(f"Saved: {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Canadian legal immigration data")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset name (e.g. 'FC', 'RAD')")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the processed CSV file")
    args = parser.parse_args()
    process_dataset(args.dataset, args.output_dir)