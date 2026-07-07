# utils/medical_sources.py – Medical reference catalog for WHO, CDC, and NHS

CLINICAL_CATALOG = {
    "viral fever": {
        "WHO": {
            "title": "WHO Fact Sheet: Infectious Diseases",
            "summary": "Viral infections are a major cause of fever globally. WHO coordinates global responses to viral outbreaks and provides guidelines for supportive care.",
            "url": "https://www.who.int/health-topics/infectious-diseases"
        },
        "CDC": {
            "title": "CDC: Viral Infections & Fever Management",
            "summary": "CDC recommends monitoring body temperature and staying home until fever-free for 24 hours without the use of fever-reducing medications.",
            "url": "https://www.cdc.gov/diseases/index.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: High Temperature (Fever) in Adults",
            "summary": "NHS guides that a high temperature is usually 38°C (100.4°F) or above. It is normally a sign that your body is fighting an infection.",
            "url": "https://www.nhs.uk/conditions/fever-in-adults/"
        }
    },
    "migraine": {
        "WHO": {
            "title": "WHO: Headache Disorders Factsheet",
            "summary": "Migraine is a primary headache disorder, most common between the ages of 35 and 45. It is twice as common in women as in men.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/headache-disorders"
        },
        "CDC": {
            "title": "CDC: Chronic Pain and Migraine Management",
            "summary": "CDC discusses health impacts of chronic migraines and supports non-pharmacological therapies as well as medical consultations.",
            "url": "https://www.cdc.gov/acute-pain/migraine/index.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Migraine Overview",
            "summary": "NHS describes migraine as a moderate or severe headache felt as a throbbing pain on one side of the head, often with nausea and light sensitivity.",
            "url": "https://www.nhs.uk/conditions/migraine/"
        }
    },
    "common cold": {
        "WHO": {
            "title": "WHO: Upper Respiratory Infections",
            "summary": "The common cold is a self-limiting viral infection of the upper respiratory tract. WHO guidelines emphasize hand hygiene to prevent spread.",
            "url": "https://www.who.int/teams/health-product-policy-and-standards"
        },
        "CDC": {
            "title": "CDC: Common Colds: Protect Yourself and Others",
            "summary": "Colds are the main reason that children miss school and adults miss work. Most adults have 2-3 colds per year, resolving in 7-10 days.",
            "url": "https://www.cdc.gov/features/rhinoviruses/index.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Common Cold",
            "summary": "NHS states that a cold is mild and usually gets better in 1 to 2 weeks. Rest, hydration, and OTC decongestants are key to relief.",
            "url": "https://www.nhs.uk/conditions/common-cold/"
        }
    },
    "cardiac concern": {
        "WHO": {
            "title": "WHO: Cardiovascular Diseases (CVDs) Factsheet",
            "summary": "CVDs are the leading cause of death globally. Early detection, lifestyle counseling, and medication can prevent heart attacks and strokes.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/cardiovascular-diseases-(cvds)"
        },
        "CDC": {
            "title": "CDC: Heart Disease Symptoms & Risk Factors",
            "summary": "CDC states that chest pain or discomfort (angina) is the most common symptom of coronary artery disease, requiring immediate medical care.",
            "url": "https://www.cdc.gov/heartdisease/signs_symptoms.htm"
        },
        "NHS": {
            "title": "NHS Health A-Z: Coronary Heart Disease",
            "summary": "NHS guides that coronary heart disease is a major cause of death. Chest tightness or pain (angina) is triggered by arterial narrowness.",
            "url": "https://www.nhs.uk/conditions/coronary-heart-disease/"
        }
    },
    "gastroenteritis (food poisoning)": {
        "WHO": {
            "title": "WHO: Foodborne Diseases and Diarrheal Prevention",
            "summary": "Foodborne diarrheal diseases affect millions annually. Safe food handling and oral rehydration therapy (ORS) are primary WHO interventions.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/food-safety"
        },
        "CDC": {
            "title": "CDC: Food Poisoning Symptoms & Treatment",
            "summary": "Most people recover from food poisoning without treatment. CDC recommends drinking plenty of fluids to prevent dehydration.",
            "url": "https://www.cdc.gov/foodsafety/symptoms.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Food Poisoning",
            "summary": "Food poisoning is common and usually gets better within a few days. The most important treatment is drinking plenty of water or ORS.",
            "url": "https://www.nhs.uk/conditions/food-poisoning/"
        }
    },
    "acid reflux / gastritis": {
        "WHO": {
            "title": "WHO: Digestive Health Guidelines",
            "summary": "Gastroesophageal reflux is common worldwide. Dietary adjustments, smoking cessation, and weight reduction are standard clinical guidelines.",
            "url": "https://www.who.int/publications/i/item/9789241565578"
        },
        "CDC": {
            "title": "CDC: Heartburn and Gerd Health Factors",
            "summary": "GERD is associated with lifestyle factors. CDC supports patient education on tracking food triggers and eating smaller portions.",
            "url": "https://www.cdc.gov/genomics/resources/diseases/gerd.htm"
        },
        "NHS": {
            "title": "NHS Health A-Z: Heartburn and Acid Reflux",
            "summary": "Heartburn is a burning feeling in the chest caused by stomach acid travelling up towards the throat. NHS suggests simple lifestyle edits.",
            "url": "https://www.nhs.uk/conditions/heartburn-and-acid-reflux/"
        }
    },
    "musculoskeletal pain": {
        "WHO": {
            "title": "WHO: Musculoskeletal Conditions Factsheet",
            "summary": "Musculoskeletal conditions are the leading contributor to disability worldwide, with low back pain being the single leading cause.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/musculoskeletal-conditions"
        },
        "CDC": {
            "title": "CDC: Arthritis and Joint Pain Information",
            "summary": "Physical activity can reduce pain and improve function, mobility, and mood for adults with arthritis and chronic joint pain.",
            "url": "https://www.cdc.gov/arthritis/basics/joint-pain.htm"
        },
        "NHS": {
            "title": "NHS Health A-Z: Joint Pain",
            "summary": "NHS guides that joint pain is common and usually clears up after a few weeks. Gentle exercises and warm baths can help relieve pain.",
            "url": "https://www.nhs.uk/conditions/joint-pain/"
        }
    },
    "dermatological condition": {
        "WHO": {
            "title": "WHO: Skin Diseases and Rashes",
            "summary": "Skin diseases affect up to 900 million people at any time. WHO recommends hygiene and avoiding allergens for non-communicable rashes.",
            "url": "https://www.who.int/teams/control-of-neglected-tropical-diseases/skin-ntds"
        },
        "CDC": {
            "title": "CDC: Eczema and Contact Dermatitis Basics",
            "summary": "CDC states that contact dermatitis occurs when the skin comes into contact with an allergen or irritant. Patch testing is recommended.",
            "url": "https://www.cdc.gov/niosh/topics/skin/default.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Eczema (Atopic)",
            "summary": "Atopic eczema is a condition that causes dry, red, itchy, and cracked skin. NHS recommends using emollients daily to keep skin moist.",
            "url": "https://www.nhs.uk/conditions/atopic-eczema/"
        }
    },
    "anxiety / stress disorder": {
        "WHO": {
            "title": "WHO: Mental Health and Anxiety Disorders",
            "summary": "Anxiety disorders are the most common mental disorders globally, characterized by excessive fear and worry. Cognitive behavioral therapy is recommended.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response"
        },
        "CDC": {
            "title": "CDC: Stress and Coping Strategies",
            "summary": "Managing stress is vital for physical health. CDC promotes mindfulness, healthy sleep patterns, and talking to a mental health professional.",
            "url": "https://www.cdc.gov/mentalhealth/stress-coping/index.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Generalized Anxiety Disorder",
            "summary": "Anxiety is a feeling of unease, such as worry or fear, that can be mild or severe. NHS advises therapy and self-care exercises.",
            "url": "https://www.nhs.uk/mental-health/conditions/generalized-anxiety-disorder/"
        }
    },
    "asthma / respiratory issue": {
        "WHO": {
            "title": "WHO: Asthma Factsheet",
            "summary": "Asthma is a major non-communicable disease affecting children and adults. WHO supports inhalation therapy to control symptoms.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/asthma"
        },
        "CDC": {
            "title": "CDC: Asthma Management & Clean Air",
            "summary": "CDC recommends creating an Asthma Action Plan with a doctor, tracking triggers like smoke, mold, dust mites, and pet dander.",
            "url": "https://www.cdc.gov/asthma/default.htm"
        },
        "NHS": {
            "title": "NHS Health A-Z: Asthma",
            "summary": "Asthma is a common lung condition that causes occasional breathing difficulties. Inhalers are the main treatment to prevent attacks.",
            "url": "https://www.nhs.uk/conditions/asthma/"
        }
    },
    "hypertension (high blood pressure)": {
        "WHO": {
            "title": "WHO: Hypertension Factsheet",
            "summary": "Hypertension is a serious medical condition that significantly increases the risks of heart, brain, kidney, and other diseases.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/hypertension"
        },
        "CDC": {
            "title": "CDC: High Blood Pressure Facts",
            "summary": "Nearly half of adults in the United States have hypertension. CDC advises eating a low-sodium diet and staying physically active.",
            "url": "https://www.cdc.gov/bloodpressure/index.htm"
        },
        "NHS": {
            "title": "NHS Health A-Z: High Blood Pressure (Hypertension)",
            "summary": "High blood pressure is common. NHS recommends eating less salt, reducing alcohol intake, and getting regular readings to monitor risk.",
            "url": "https://www.nhs.uk/conditions/high-blood-pressure-hypertension/"
        }
    },
    "diabetes risk": {
        "WHO": {
            "title": "WHO: Diabetes Factsheet",
            "summary": "Diabetes is a chronic metabolic disease characterized by elevated levels of blood glucose. Healthy diet and exercise prevent Type 2 diabetes.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes"
        },
        "CDC": {
            "title": "CDC: Prevent Diabetes and Track Blood Sugar",
            "summary": "CDC guides that early screening for prediabetes is key. Losing a small amount of weight and doing regular exercise reduces diabetes risk by 58%.",
            "url": "https://www.cdc.gov/diabetes/index.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Type 2 Diabetes",
            "summary": "Type 2 diabetes causes high sugar levels. NHS outlines that early symptoms like frequent urination and fatigue can be managed through diet.",
            "url": "https://www.nhs.uk/conditions/type-2-diabetes/"
        }
    },
    "ent (ear, nose & throat) issue": {
        "WHO": {
            "title": "WHO: Ear and Hearing Care",
            "summary": "Unaddressed hearing loss and ear infections can lead to speech impairments. WHO promotes immunizations and proper hygiene.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/deafness-and-hearing-loss"
        },
        "CDC": {
            "title": "CDC: Ear Infections (Otitis Media)",
            "summary": "Ear infections occur when fluid builds up behind the eardrum. CDC advises on antibiotic stewardship, as many are viral.",
            "url": "https://www.cdc.gov/antibiotic-use/ear-infection.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Ear Infections",
            "summary": "Ear infections are common, especially in children. NHS states they usually get better on their own within 3 days without antibiotics.",
            "url": "https://www.nhs.uk/conditions/ear-infections/"
        }
    },
    "gynecological issue": {
        "WHO": {
            "title": "WHO: Female Reproductive Health",
            "summary": "Access to quality gynecological care reduces maternal and reproductive morbidity. WHO recommends annual screenings.",
            "url": "https://www.who.int/health-topics/women-s-health"
        },
        "CDC": {
            "title": "CDC: Gynecologic Health and Cancers",
            "summary": "CDC outlines symptoms of pelvic disorders and cancers, recommending immediate evaluation for abnormal vaginal bleeding.",
            "url": "https://www.cdc.gov/cancer/gynecologic/index.htm"
        },
        "NHS": {
            "title": "NHS Health A-Z: Period Pain & Pelvic Care",
            "summary": "Period pain is common. NHS recommends heat therapy, mild pain relievers, and seeing a doctor if pelvic pain is severe or sudden.",
            "url": "https://www.nhs.uk/conditions/period-pain/"
        }
    },
    "ophthalmic issue": {
        "WHO": {
            "title": "WHO: Blindness and Vision Impairment",
            "summary": "Globally, at least 2.2 billion people have a near or distance vision impairment. WHO promotes early screening for refractive errors.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment"
        },
        "CDC": {
            "title": "CDC: Conjunctivitis (Pink Eye) Overview",
            "summary": "Conjunctivitis is swelling of the conjunctiva. CDC outlines that viral and bacterial conjunctivitis are highly contagious.",
            "url": "https://www.cdc.gov/conjunctivitis/index.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Red Eye and Conjunctivitis",
            "summary": "NHS guides that red eyes are usually caused by minor infections or dry eyes. Rinse with cool water and avoid wearing contact lenses.",
            "url": "https://www.nhs.uk/conditions/red-eye/"
        }
    },
    "urinary tract infection (uti)": {
        "WHO": {
            "title": "WHO: Urinary Infections and AMR",
            "summary": "UTIs are among the most common bacterial infections. WHO alerts that increasing antibiotic resistance requires careful stewardship.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance"
        },
        "CDC": {
            "title": "CDC: Urinary Tract Infections Facts",
            "summary": "UTIs are caused by bacteria getting into the urinary tract. CDC recommends drinking lots of water to flush bacteria out.",
            "url": "https://www.cdc.gov/antibiotic-use/uti.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Urinary Tract Infections",
            "summary": "UTIs affect the bladder or kidneys. NHS states they are treated with antibiotics and drinking water helps relieve burning symptoms.",
            "url": "https://www.nhs.uk/conditions/urinary-tract-infections-utis/"
        }
    },
    "fatigue / anemia": {
        "WHO": {
            "title": "WHO: Anaemia Overview Facts",
            "summary": "Anaemia is a serious global public health problem that particularly affects young children and pregnant women, often caused by iron deficiency.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/anaemia"
        },
        "CDC": {
            "title": "CDC: Iron Deficiency and Anemia Basics",
            "summary": "Iron deficiency occurs when your body doesn't have enough iron, which is the most common cause of anemia and tiredness.",
            "url": "https://www.cdc.gov/ncbddd/blooddisorders/anemia/index.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: Iron Deficiency Anaemia",
            "summary": "NHS guides that iron deficiency anaemia is treated with iron tablets and eating iron-rich foods, which helps resolve chronic fatigue.",
            "url": "https://www.nhs.uk/conditions/iron-deficiency-anaemia/"
        }
    },
    "influenza": {
        "WHO": {
            "title": "WHO Fact Sheet: Influenza (Seasonal)",
            "summary": "Seasonal influenza is an acute respiratory infection caused by influenza viruses. It circulates in all parts of the world and causes severe illness.",
            "url": "https://www.who.int/news-room/fact-sheets/detail/influenza-(seasonal)"
        },
        "CDC": {
            "title": "CDC: Key Facts About Influenza (Flu)",
            "summary": "Influenza is a contagious respiratory illness caused by influenza viruses. CDC recommends an annual flu vaccine as the first and best line of defense.",
            "url": "https://www.cdc.gov/flu/about/keyfacts.htm"
        },
        "NHS": {
            "title": "NHS Health A-Z: Flu",
            "summary": "Flu is a common infectious viral illness spread by coughs and sneezes. It usually clears up in a week with rest and warmth.",
            "url": "https://www.nhs.uk/conditions/flu/"
        }
    },
    "covid-19": {
        "WHO": {
            "title": "WHO: Coronavirus Disease (COVID-19)",
            "summary": "COVID-19 is an infectious disease caused by the SARS-CoV-2 virus. Most people will experience mild to moderate respiratory illness and recover.",
            "url": "https://www.who.int/health-topics/coronavirus"
        },
        "CDC": {
            "title": "CDC: COVID-19 Symptoms and Testing",
            "summary": "CDC guides that symptoms include fever, cough, fatigue, and loss of taste or smell. Isolation and testing are recommended for suspected cases.",
            "url": "https://www.cdc.gov/coronavirus/2019-ncov/index.html"
        },
        "NHS": {
            "title": "NHS Health A-Z: COVID-19 Symptoms and Guidance",
            "summary": "NHS lists key symptoms of COVID-19, recommending resting at home, drinking fluids, and avoiding contact with vulnerable individuals.",
            "url": "https://www.nhs.uk/conditions/covid-19/"
        }
    }
}

DEFAULT_CATALOG = {
    "WHO": {
        "title": "World Health Organization (WHO) Guidelines",
        "summary": "WHO provides global health standards, factsheets, and guidelines for managing general health conditions.",
        "url": "https://www.who.int"
    },
    "CDC": {
        "title": "Centers for Disease Control and Prevention (CDC)",
        "summary": "CDC offers public health advice, vaccination schedules, and disease tracking guidelines.",
        "url": "https://www.cdc.gov"
    },
    "NHS": {
        "title": "NHS Choices Health A-Z",
        "summary": "NHS provides patient-friendly health advice, disease directories, and self-care plans.",
        "url": "https://www.nhs.uk"
    }
}

def retrieve_sources(condition_name: str) -> dict:
    """
    Fuzzy-matches a condition name to retrieve structured WHO, CDC, and NHS citations.
    """
    c_lower = condition_name.lower()
    for key, sources in CLINICAL_CATALOG.items():
        if key in c_lower or c_lower in key:
            return sources
    
    # Check individual words for partial match
    words = c_lower.split()
    for word in words:
        if len(word) < 4:
            continue
        for key, sources in CLINICAL_CATALOG.items():
            if word in key:
                return sources
                
    return DEFAULT_CATALOG
