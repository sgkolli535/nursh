"""
Evidence citations for health rules and nutrient pairings.
Every health context rule and nutrient pairing links to published evidence.
These are established science, not novel claims.
"""

EVIDENCE_CITATIONS = [
    # === Nutrient Pairings ===
    {
        "claim": "Iron absorption is enhanced by vitamin C",
        "citation_text": "Hallberg L, Brune M, Rossander L. Iron absorption in man: ascorbic acid and dose-dependent inhibition by phytate. Am J Clin Nutr. 1989;49(1):140-144. Cook JD, Reddy MB. Effect of ascorbic acid intake on nonheme-iron absorption from a complete diet. Am J Clin Nutr. 2001;73(1):93-98.",
        "doi": "10.1093/ajcn/73.1.93",
        "rule_key": "pairing_iron_vitamin_c",
        "display_text": "Research shows that eating vitamin C-rich foods alongside iron-rich foods helps your body absorb more iron.",
    },
    {
        "claim": "Calcium inhibits iron absorption when consumed together",
        "citation_text": "Hallberg L, Rossander-Hulthén L, Brune M, Gleerup A. Calcium and iron absorption: mechanism of action and nutritional importance. Eur J Clin Nutr. 1992;46(5):317-327.",
        "doi": "10.1038/sj.ejcn.1600750",
        "rule_key": "pairing_calcium_iron_inhibitor",
        "display_text": "Calcium can reduce iron absorption when eaten at the same time. Spacing them out across different meals helps both nutrients work better.",
    },
    {
        "claim": "Tannins in tea and coffee inhibit iron absorption",
        "citation_text": "Hurrell RF, Reddy M, Cook JD. Inhibition of non-haem iron absorption in man by polyphenolic-containing beverages. Br J Nutr. 1999;81(4):289-295.",
        "doi": "10.1017/S0007114599000537",
        "rule_key": "pairing_tannin_iron_inhibitor",
        "display_text": "The tannins in tea and coffee can reduce iron absorption. Waiting an hour before or after meals to drink them helps.",
    },
    # === PCOS ===
    {
        "claim": "Anti-inflammatory diets may improve PCOS symptoms",
        "citation_text": "Barrea L, et al. Adherence to the Mediterranean diet, dietary patterns and body composition in women with polycystic ovary syndrome (PCOS). Nutrients. 2019;11(10):2278.",
        "doi": "10.3390/nu11102278",
        "rule_key": "pcos_anti_inflammatory",
        "display_text": "Studies suggest that anti-inflammatory foods — like those rich in omega-3s, leafy greens, and berries — may support hormonal balance in PCOS.",
    },
    {
        "claim": "Inositol-rich foods may support insulin sensitivity in PCOS",
        "citation_text": "Unfer V, et al. Myo-inositol effects in women with PCOS: a meta-analysis of randomized controlled trials. Endocr Connect. 2017;6(8):647-658.",
        "doi": "10.1530/EC-17-0243",
        "rule_key": "pcos_inositol",
        "display_text": "Inositol, found in foods like citrus fruits, beans, and whole grains, has been studied for its role in supporting insulin sensitivity.",
    },
    # === Iron-Deficiency Anemia ===
    {
        "claim": "Heme iron from animal sources has higher bioavailability than non-heme iron",
        "citation_text": "Hurrell R, Egli I. Iron bioavailability and dietary reference values. Am J Clin Nutr. 2010;91(5):1461S-1467S.",
        "doi": "10.3945/ajcn.2010.28674F",
        "rule_key": "anemia_heme_iron",
        "display_text": "Iron from animal sources (heme iron) is absorbed more readily than plant-based iron. Pairing plant iron with vitamin C helps bridge the gap.",
    },
    # === Hypothyroidism ===
    {
        "claim": "Selenium supports thyroid hormone metabolism",
        "citation_text": "Rayman MP. Selenium and human health. Lancet. 2012;379(9822):1256-1268.",
        "doi": "10.1016/S0140-6736(11)61452-9",
        "rule_key": "hypothyroidism_selenium",
        "display_text": "Selenium plays a role in thyroid hormone production. Brazil nuts, fish, and eggs are good sources.",
    },
    {
        "claim": "Cruciferous vegetables and thyroid: context matters",
        "citation_text": "Felker P, Bunch R, Leung AM. Concentrations of thiocyanate and goitrin in human plasma, their precursor concentrations in brassica vegetables, and associated potential risk for hypothyroidism. Nutr Rev. 2016;74(4):248-258.",
        "doi": "10.1093/nutrit/nuv110",
        "rule_key": "hypothyroidism_cruciferous",
        "display_text": "Cruciferous vegetables (broccoli, cauliflower) are nutritious and generally safe. Cooking them reduces goitrogen content significantly.",
    },
    # === Pregnancy ===
    {
        "claim": "Folate is critical for neural tube development in early pregnancy",
        "citation_text": "MRC Vitamin Study Research Group. Prevention of neural tube defects: results of the Medical Research Council Vitamin Study. Lancet. 1991;338(8760):131-137.",
        "doi": "10.1016/0140-6736(91)90133-A",
        "rule_key": "pregnancy_folate",
        "display_text": "Folate is especially important in early pregnancy for healthy development. Lentils, leafy greens, and fortified foods are rich sources.",
    },
    {
        "claim": "High-mercury fish should be limited during pregnancy",
        "citation_text": "FDA/EPA. Advice about Eating Fish: For Those Who Might Become or Are Pregnant or Breastfeeding and Children Ages 1-11 Years. 2021.",
        "doi": None,
        "rule_key": "pregnancy_mercury_fish",
        "display_text": "During pregnancy, it's best to choose low-mercury fish like sardines and salmon. Higher-mercury fish like swordfish and king mackerel are best limited.",
    },
    # === Type 2 Diabetes ===
    {
        "claim": "High-fiber, low-glycemic foods improve glycemic control",
        "citation_text": "Chandalia M, et al. Beneficial effects of high dietary fiber intake in patients with type 2 diabetes mellitus. N Engl J Med. 2000;342(19):1392-1398.",
        "doi": "10.1056/NEJM200005113421903",
        "rule_key": "diabetes_fiber_glycemic",
        "display_text": "High-fiber foods like lentils, vegetables, and whole grains help maintain steady blood sugar levels.",
    },
    # === Perimenopause ===
    {
        "claim": "Phytoestrogens may help manage menopausal symptoms",
        "citation_text": "Taku K, et al. Extracted or synthesized soybean isoflavones reduce menopausal hot flash frequency and severity. Menopause. 2012;19(7):776-790.",
        "doi": "10.1097/gme.0b013e3182410f10",
        "rule_key": "perimenopause_phytoestrogen",
        "display_text": "Phytoestrogen-rich foods like soy, flaxseeds, and sesame may help support comfort during perimenopause.",
    },
    # === Celiac ===
    {
        "claim": "Gluten-free diet is essential for celiac disease management",
        "citation_text": "Rubio-Tapia A, et al. ACG clinical guidelines: diagnosis and management of celiac disease. Am J Gastroenterol. 2013;108(5):656-676.",
        "doi": "10.1038/ajg.2013.79",
        "rule_key": "celiac_gluten_free",
        "display_text": "For people with celiac disease, avoiding wheat, barley, and rye is essential. Many whole grains like rice, millet, and quinoa are naturally gluten-free.",
    },
]
