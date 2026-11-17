import os
import json
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.chunking import TextChunker
from app.services.retrieval import VectorStoreService

logger = logging.getLogger("healthsutra.ingestion")

# Authentic, verified seed knowledge base for WHO & Indian Government Health Programmes
SEED_VERIFIED_DOCUMENTS = [
    {
        "id": "WHO_DENGUE_2024",
        "title": "Dengue and Severe Dengue Fact Sheet",
        "organization": "WHO",
        "document_type": "fact_sheet",
        "disease_category": "Vector-Borne Diseases",
        "publication_date": "2024-04-23",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue",
        "language": "en",
        "pages": [
            {
                "page": 1,
                "text": """Dengue is a viral infection transmitted to humans through the bite of infected mosquitoes, primarily Aedes aegypti and, to a lesser extent, Aedes albopictus. The virus responsible is the dengue virus (DENV), comprising four distinct serotypes (DENV-1, DENV-2, DENV-3, and DENV-4). While many DENV infections are asymptomatic or produce only mild illness, DENV can cause severe flu-like illness and occasionally develops into a potentially lethal complication called severe dengue. Global incidence has grown dramatically in recent decades, with about half of the world's population now at risk."""
            },
            {
                "page": 2,
                "text": """Dengue Symptoms: Most people with dengue have mild or no symptoms and will get better in 1-2 weeks. When symptoms occur, they usually begin 4-10 days after infection and last for 2-7 days. Symptoms may include: high fever (40°C/104°F), severe headache, pain behind the eyes (retro-orbital pain), muscle and joint pains, nausea, vomiting, swollen glands, and rash. Individuals who are infected for the second time are at greater risk of severe dengue."""
            },
            {
                "page": 3,
                "text": """Severe Dengue Warning Signs: Severe dengue is a medical emergency that can lead to plasma leakage, fluid accumulation, respiratory distress, severe bleeding, or organ impairment. Warning signs develop 3-7 days after first symptoms, often when the fever is dropping. Warning signs include: severe abdominal pain, persistent vomiting, rapid breathing, bleeding gums or nose, fatigue, restlessness, liver enlargement, and blood in vomit or stool. Patients with these symptoms need immediate hospital care."""
            },
            {
                "page": 4,
                "text": """Prevention and Mosquito Control: The primary method of controlling or preventing the transmission of dengue virus is to combat mosquito vectors. This includes preventing mosquitoes from accessing egg-laying habitats by environmental management and source reduction; disposing of solid waste properly and removing artificial man-made habitats that can hold water (e.g. buckets, discarded tyres, flower vases); covering, emptying, and cleaning domestic water storage containers on a weekly basis; using window screens, mosquito repellents, coils, and vaporizers, and wearing protective clothing that minimizes skin exposure."""
            },
            {
                "page": 5,
                "text": """Treatment and Clinical Management: There is no specific antiviral treatment for dengue fever. Patients should rest, stay hydrated by drinking plenty of clean fluids and oral rehydration solutions, and seek medical advice. For pain relief and fever reduction, paracetamol (acetaminophen) is recommended. Non-steroidal anti-inflammatory drugs (NSAIDs) such as ibuprofen and aspirin must be strictly avoided because they thin the blood and can exacerbate bleeding risks."""
            }
        ]
    },
    {
        "id": "WHO_MALARIA_2024",
        "title": "Malaria Key Facts and Clinical Guidelines",
        "organization": "WHO",
        "document_type": "fact_sheet",
        "disease_category": "Vector-Borne Diseases",
        "publication_date": "2024-03-27",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/malaria",
        "language": "en",
        "pages": [
            {
                "page": 1,
                "text": """Malaria is a life-threatening disease caused by Plasmodium parasites that are spread to people through the bites of infected female Anopheles mosquitoes. Five parasite species cause malaria in humans, with Plasmodium falciparum and Plasmodium vivax posing the greatest threat. P. falciparum is the deadliest malaria parasite and the most prevalent on the African continent, while P. vivax is the dominant malaria parasite in most countries outside sub-Saharan Africa, including India."""
            },
            {
                "page": 2,
                "text": """Malaria Symptoms: The first symptoms of malaria are fever, headache, and chills. Symptoms usually appear 10-15 days after the mosquito bite. In infants and children, severe anaemia, respiratory distress in relation to metabolic acidosis, or cerebral malaria are frequent. In adults, multi-organ failure is also frequent. If not treated within 24 hours, P. falciparum malaria can progress to severe illness and death."""
            },
            {
                "page": 3,
                "text": """Prevention of Malaria: Vector control is the main way to prevent and reduce malaria transmission. Two forms of vector control are effective in a wide range of settings: insecticide-treated nets (ITNs) and indoor residual spraying (IRS). Sleeping under an ITN can reduce contact between mosquitoes and humans by providing both a physical barrier and an insecticidal effect. Community awareness to eliminate stagnant water puddles prevents Anopheles breeding."""
            }
        ]
    },
    {
        "id": "MOHFW_TB_NTEP_2024",
        "title": "National Tuberculosis Elimination Programme (NTEP) Guidelines",
        "organization": "MoHFW",
        "document_type": "guideline",
        "disease_category": "Respiratory Diseases",
        "publication_date": "2024-01-15",
        "source_url": "https://tbcindia.gov.in/index1.php?sublinkid=4153&level=1&lid=2798",
        "language": "en",
        "pages": [
            {
                "page": 1,
                "text": """Tuberculosis (TB) is an infectious airborne disease caused by Mycobacterium tuberculosis that primarily affects the lungs (pulmonary TB). India bears the highest TB burden globally, and the Government of India through the National Tuberculosis Elimination Programme (NTEP) aims to eliminate TB by 2025. TB spreads through the air when people who have active pulmonary TB cough, sneeze, or spit."""
            },
            {
                "page": 2,
                "text": """Key Symptoms of Pulmonary TB: Persistent cough lasting for 2 weeks or more, accompanied by production of sputum or blood in sputum (hemoptysis); unexplained fever, particularly in the evening; night sweats; significant unintentional weight loss; loss of appetite; chest pain and general fatigue. Any individual with a cough for two weeks or more must undergo free sputum examination and CBNAAT/Truenat molecular testing at the nearest Government Designated Microscopy Centre (DMC) or Primary Health Centre (PHC)."""
            },
            {
                "page": 3,
                "text": """Treatment and Ni-kshay Poshan Yojana: Under NTEP, diagnosis and full-course Directly Observed Treatment (DOTS) are provided 100% free of charge at all public health facilities across India. Patients receive financial nutritional support of Rs 500 per month through Direct Benefit Transfer under the Ni-kshay Poshan Yojana for each month of active treatment. It is critical that patients complete the full prescribed 6-month regimen even after feeling better, to avoid developing drug-resistant TB (MDR-TB)."""
            }
        ]
    },
    {
        "id": "MOHFW_MATERNAL_CHILD_2024",
        "title": "National Health Mission: Maternal, Infant and Young Child Nutrition",
        "organization": "MoHFW",
        "document_type": "guideline",
        "disease_category": "Maternal and Child Health",
        "publication_date": "2024-02-10",
        "source_url": "https://nhm.gov.in/index1.php?lang=1&level=2&sublinkid=842&lid=311",
        "language": "en",
        "pages": [
            {
                "page": 1,
                "text": """Infant and Young Child Feeding (IYCF) Guidelines: The Ministry of Health and Family Welfare and National Health Mission mandate that breastfeeding should be initiated within the first hour of birth (early initiation). Colostrum (the first yellowish thick milk) is rich in antibodies and provides vital early immunity against diarrhea and respiratory infections. It should never be discarded."""
            },
            {
                "page": 2,
                "text": """Exclusive Breastfeeding: Infants must be exclusively breastfed for the first six months of life (180 days). No other food or liquid, not even water, should be given during this period because breast milk provides all the hydration and nutrition a baby needs. At 6 months of age, complementary feeding should be introduced along with continued breastfeeding up to 2 years of age or beyond. Complementary foods must be hygienically prepared, age-appropriate, nutrient-dense, and made from local grains, pulses, vegetables, and fruits."""
            },
            {
                "page": 3,
                "text": """Maternal Health & Iron Folic Acid (IFA) Supplementation: Pregnant women are advised to undergo at least 4 antenatal checkups (ANCs) under Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA). To prevent maternal anaemia, pregnant women should take 100 Iron and Folic Acid (IFA) tablets starting from the second trimester (after 14 weeks of pregnancy), and continued during the postpartum period for at least 180 days."""
            }
        ]
    },
    {
        "id": "WHO_HEATWAVE_GUIDELINES",
        "title": "Public Health Advice on Heatwaves and Heat-Related Illness",
        "organization": "WHO",
        "document_type": "advisory",
        "disease_category": "Environmental Health",
        "publication_date": "2024-05-18",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/heatwaves-and-health",
        "language": "en",
        "pages": [
            {
                "page": 1,
                "text": """Extreme heat exposure can cause severe heat-related illnesses including heat cramps, heat exhaustion, and heat stroke. Heat stroke is a medical emergency with high body temperature (above 40°C), confusion, hot dry skin, and unconsciousness. During heatwaves: keep your home cool, avoid going outside during the hottest hours (11:00 AM to 4:00 PM), stay in the shade, drink cool water regularly before feeling thirsty, avoid alcoholic and sugary drinks, wear loose lightweight cotton clothing, and never leave children or pets in parked vehicles."""
            }
        ]
    }
]

class IngestionManager:
    def __init__(self):
        self.chunker = TextChunker()
        self.vector_store = VectorStoreService.get_instance()
        self.registry_path = settings.DOCUMENT_REGISTRY_PATH
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading document registry ({e}). Starting fresh.")
        return {}

    def _save_registry(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)

    def extract_pdf_pages(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text page by page from an uploaded PDF using PyMuPDF."""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            pages = []
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                text = page.get_text("text")
                if text.strip():
                    pages.append({
                        "page": page_idx + 1,
                        "text": text
                    })
            return pages
        except Exception as e:
            logger.error(f"PyMuPDF error reading {pdf_path}: {e}")
            return []

    def ingest_document_data(
        self,
        doc_id: str,
        title: str,
        organization: str,
        doc_type: str,
        category: str,
        pub_date: str,
        url: str,
        pages: List[Dict[str, Any]],
        language: str = "en",
        file_path: str = ""
    ) -> int:
        """Chunks and indexes an approved document into FAISS and registry."""
        all_chunks = []
        for page_data in pages:
            page_num = page_data.get("page", 1)
            raw_text = page_data.get("text", "")
            page_chunks = self.chunker.chunk_page_content(
                document_id=doc_id,
                document_title=title,
                organization=organization,
                page_number=page_num,
                raw_text=raw_text,
                source_url=url
            )
            all_chunks.extend(page_chunks)

        if not all_chunks:
            logger.warning(f"No valid chunks generated for document {doc_id}")
            return 0

        # Index in FAISS
        added = self.vector_store.add_chunks(all_chunks)

        # Update registry
        self.registry[doc_id] = {
            "id": doc_id,
            "title": title,
            "organization": organization,
            "document_type": doc_type,
            "disease_category": category,
            "publication_date": pub_date,
            "source_url": url,
            "file_path": file_path,
            "verified": True,
            "language": language,
            "chunks_count": len(all_chunks)
        }
        self._save_registry()
        logger.info(f"Document {doc_id} ('{title}') ingested with {len(all_chunks)} chunks.")
        return added

    def seed_initial_knowledge(self) -> int:
        """Seeds the system with authenticated WHO & MoHFW publications."""
        total_chunks = 0
        for doc in SEED_VERIFIED_DOCUMENTS:
            doc_id = doc["id"]
            if doc_id not in self.registry:
                logger.info(f"Seeding verified document: {doc_id} ({doc['title']})...")
                chunks_added = self.ingest_document_data(
                    doc_id=doc_id,
                    title=doc["title"],
                    organization=doc["organization"],
                    doc_type=doc["document_type"],
                    category=doc["disease_category"],
                    pub_date=doc["publication_date"],
                    url=doc["source_url"],
                    pages=doc["pages"],
                    language=doc.get("language", "en")
                )
                total_chunks += chunks_added
            else:
                logger.info(f"Document {doc_id} already registered.")
        return total_chunks

    def list_documents(self) -> List[Dict[str, Any]]:
        return list(self.registry.values())
