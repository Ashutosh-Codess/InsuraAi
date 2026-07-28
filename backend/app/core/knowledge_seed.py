"""
Seeds the Chroma vector DB with insurance knowledge base documents on first
startup. This gives the RAG retriever real content to search, so the copilot
can ground its answers instead of hallucinating.

Call seed_knowledge_base() from startup_event() in main.py AFTER the embedding
model is loaded - both functions are idempotent (skip if data already exists).
"""
import logging

from rag.embeddings import embed_texts
from vector_db.client import get_or_create_collection

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sample knowledge base documents per collection
# ---------------------------------------------------------------------------

POLICY_TERMS_DOCS = [
    {
        "id": "pt-001",
        "text": "Water damage coverage: Home insurance policies cover sudden and accidental water damage from burst pipes, appliance overflow, and roof leaks from storms. Gradual water damage (e.g., slow pipe leaks known to the homeowner) is excluded. Flood damage caused by external rising water requires a separate flood insurance policy.",
        "metadata": {"source": "policy_terms", "section": "water_damage"},
    },
    {
        "id": "pt-002",
        "text": "Health insurance inpatient coverage: Inpatient hospitalisation is covered up to the policy sum insured after the deductible is met. Room rent is capped at 1% of sum insured per day unless the policy specifies a higher limit. Pre-existing diseases are covered after a waiting period of 24-48 months depending on the insurer.",
        "metadata": {"source": "policy_terms", "section": "health_inpatient"},
    },
    {
        "id": "pt-003",
        "text": "Motor insurance third-party liability: Third-party liability coverage is mandatory under the Motor Vehicles Act. It covers bodily injury and property damage caused to a third party. Own-damage cover requires a comprehensive policy and covers collision, fire, theft, and natural calamities.",
        "metadata": {"source": "policy_terms", "section": "motor_liability"},
    },
    {
        "id": "pt-004",
        "text": "Life insurance death benefit: The sum assured is paid to the nominee upon the death of the life assured during the policy term. Death by suicide within the first year of the policy is typically excluded. Accidental death may qualify for an additional accidental death benefit rider.",
        "metadata": {"source": "policy_terms", "section": "life_death_benefit"},
    },
    {
        "id": "pt-005",
        "text": "Travel insurance medical emergency: Medical emergency coverage includes hospitalisation, emergency medical evacuation, and repatriation of remains. Coverage is valid only when the insured is travelling outside their country of residence. Pre-existing conditions are excluded unless specifically declared and accepted.",
        "metadata": {"source": "policy_terms", "section": "travel_medical"},
    },
    {
        "id": "pt-006",
        "text": "Exclusions common to all policies: All policies exclude claims arising from war, invasion, civil war, nuclear contamination, intentional self-harm, participation in criminal activity, and hazardous adventure sports unless an applicable rider is purchased.",
        "metadata": {"source": "policy_terms", "section": "general_exclusions"},
    },
    {
        "id": "pt-007",
        "text": "Claim filing timeline: Claims must be filed within 30 days of the incident for health and motor policies. Late filing may result in claim rejection unless the delay is due to circumstances beyond the insured's control. Emergency hospitalisation must be notified within 24 hours.",
        "metadata": {"source": "policy_terms", "section": "claim_timeline"},
    },
    {
        "id": "pt-008",
        "text": "Renewal and lapse: Policies must be renewed before the expiry date to maintain continuous coverage. A grace period of 15-30 days is typically provided. Claims for incidents that occur during a lapsed period are not covered even if the policy is later renewed.",
        "metadata": {"source": "policy_terms", "section": "renewal"},
    },
]

MEDICAL_RULES_DOCS = [
    {
        "id": "mr-001",
        "text": "Daycare procedures: Over 540 daycare procedures are covered under health insurance policies without requiring 24-hour hospitalisation. These include cataract surgery, chemotherapy, dialysis, and arthroscopy. The list varies by insurer and policy version.",
        "metadata": {"source": "medical_rules", "section": "daycare"},
    },
    {
        "id": "mr-002",
        "text": "Pre-existing disease (PED) waiting period: Conditions diagnosed or treated within 48 months before the policy start date are considered pre-existing. Standard waiting period is 2-4 years. Some insurers offer zero-waiting-period PED coverage at a higher premium.",
        "metadata": {"source": "medical_rules", "section": "pre_existing"},
    },
    {
        "id": "mr-003",
        "text": "Network hospitals and cashless treatment: Cashless hospitalisation is available only at network hospitals empanelled with the insurer's TPA. Non-network hospitals require the insured to pay upfront and file a reimbursement claim within 15 days of discharge.",
        "metadata": {"source": "medical_rules", "section": "cashless"},
    },
    {
        "id": "mr-004",
        "text": "Mental health coverage: As per IRDAI guidelines (2017), health insurance policies must cover mental illness on par with physical illness. This includes inpatient treatment for conditions like depression, bipolar disorder, and schizophrenia.",
        "metadata": {"source": "medical_rules", "section": "mental_health"},
    },
    {
        "id": "mr-005",
        "text": "Maternity benefits: Maternity coverage (normal delivery and C-section) is covered after a waiting period of 9-24 months. Coverage includes pre-natal and post-natal expenses. Newborn baby cover from day one is often included as a sub-limit.",
        "metadata": {"source": "medical_rules", "section": "maternity"},
    },
]

REPAIR_ESTIMATES_DOCS = [
    {
        "id": "re-001",
        "text": "Vehicle repair cost benchmarks (India 2025): Minor dents and paint work: ₹5,000-₹15,000. Bumper replacement: ₹8,000-₹25,000. Windshield replacement: ₹10,000-₹40,000 depending on vehicle model. Engine repair (major): ₹50,000-₹2,00,000. Total loss threshold: repair cost exceeds 75% of Insured Declared Value (IDV).",
        "metadata": {"source": "repair_estimates", "section": "vehicle_benchmarks"},
    },
    {
        "id": "re-002",
        "text": "Home repair cost benchmarks (India 2025): Water damage restoration: ₹20,000-₹80,000 per room. Roof repair (partial): ₹30,000-₹1,50,000. Electrical rewiring (per room): ₹8,000-₹20,000. Structural damage assessment requires a licensed surveyor appointed by the insurer.",
        "metadata": {"source": "repair_estimates", "section": "home_benchmarks"},
    },
    {
        "id": "re-003",
        "text": "Depreciation schedule for motor claims: Vehicles 0-6 months old: 0% depreciation on parts. 6-12 months: 5%. 1-2 years: 10%. 2-3 years: 15%. 3-4 years: 25%. 4-5 years: 35%. Over 5 years: 40-50%. Zero depreciation add-on riders eliminate this deduction.",
        "metadata": {"source": "repair_estimates", "section": "depreciation"},
    },
]

REGULATORY_RULES_DOCS = [
    {
        "id": "rr-001",
        "text": "IRDAI claims settlement mandate: As per IRDAI (Insurance Regulatory and Development Authority of India) regulations, insurers must settle claims within 30 days of receiving all required documents. For complex claims requiring investigation, the period may extend to 90 days with prior intimation.",
        "metadata": {"source": "regulatory_rules", "section": "settlement_timeline"},
    },
    {
        "id": "rr-002",
        "text": "Free-look period: All new policies must offer a free-look period of 15 days (30 days for policies sold through distance marketing). The policyholder may cancel the policy and receive a full premium refund minus medical examination and stamp duty charges.",
        "metadata": {"source": "regulatory_rules", "section": "free_look"},
    },
    {
        "id": "rr-003",
        "text": "KYC requirements for insurance: PAN card or Form 60 is mandatory for policies with annual premium above ₹50,000. Aadhaar-based e-KYC is accepted. Video-based KYC (V-CIP) is permitted for remote policy issuance under IRDAI guidelines.",
        "metadata": {"source": "regulatory_rules", "section": "kyc"},
    },
    {
        "id": "rr-004",
        "text": "Grievance redressal: Policyholders may escalate unresolved claims to the Insurance Ombudsman within their jurisdiction if the insurer fails to respond within 30 days or the resolution is unsatisfactory. The Ombudsman can award up to ₹30 lakh in compensation for personal line policies.",
        "metadata": {"source": "regulatory_rules", "section": "ombudsman"},
    },
]

COLLECTION_MAP = {
    "policy_terms": POLICY_TERMS_DOCS,
    "medical_rules": MEDICAL_RULES_DOCS,
    "repair_estimates": REPAIR_ESTIMATES_DOCS,
    "regulatory_rules": REGULATORY_RULES_DOCS,
}


def _collection_is_empty(name: str) -> bool:
    """Returns True if the collection has no documents."""
    coll = get_or_create_collection(name)
    return coll.count() == 0


def seed_knowledge_base() -> None:
    """
    Seeds each Chroma collection with sample documents if it is empty.
    Safe to call repeatedly - skips collections that already have data.
    """
    for collection_name, docs in COLLECTION_MAP.items():
        if not _collection_is_empty(collection_name):
            logger.info("[knowledge_seed] %s already has data, skipping.", collection_name)
            continue

        logger.info("[knowledge_seed] Seeding %s with %d documents...", collection_name, len(docs))
        coll = get_or_create_collection(collection_name)

        texts = [d["text"] for d in docs]
        ids = [d["id"] for d in docs]
        metadatas = [d["metadata"] for d in docs]
        embeddings = embed_texts(texts)

        coll.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        logger.info("[knowledge_seed] Seeded %s OK.", collection_name)

    logger.info("[knowledge_seed] Knowledge base seeding complete.")
