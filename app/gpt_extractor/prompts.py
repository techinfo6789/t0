
entity_extraction_prompt = """Extract all key value pairs from this data, these can be the categories:
Supplier information such as Vendor name, Supplier name
Ingredient Information (extracttext or numeric)
Product information such as product name, product code
Nutrient Informations (extract numeric info first), other info
Physical Properties (extract numeric info), other info
Raw Material color (text), other info
Heavy Metals (numeric), other info
Contaminants and allergens (boolean or text), other info, 
Lab Test Definition which is The specific tests or methods used to evaluate the quality or purity of the raw material.
Extract other information mentioned as well , Give result in json format."""


entity_extraction_prompt2 = """Extract all key value pairs from this data, these can be the categories
Supplier Information (text): Vendor Name, Supplier Name, Supplier Code, Raw Material Supplier, RM Supplier Code, Key RM Identifiers
Product/Raw Material Information (text or numeric) : Name, Product Code, Ingredient Type, Potency, Category, CAS Number, Botanical Name, Active Ingredient, Active Ingredient %, Unit of Measure, Form
Nutrition Information (numeric with unit): Nutrient Values, Calories, Protein, Fat, Carbohydrates, Dietary Fiber, Vitamins, Minerals, Amino Acids
Physical Properties (numeric with unit): Technical Details, Raw Material Color, Bulk Density, Tap Density, pH, Water Activity, Loss on Drying, Residue, Soluble in
Heavy Metals (numeric): Heavy Metal Concentrations, Lead, Cadmium, Arsenic, Mercury
Contaminants and Allergens (boolean or text): Allergens, Dietary Restrictions, Non-GMO, Vegan, Kosher, Organic, NSF Sport, Prop 65, Halal, CFU, IU, Enzyme Potency
Lab Test Definitions (text): Specific tests or methods used to evaluate the quality or purity of raw materials, Assay Requirement, Excepient Pairing, Effective Dosage
Miscellaneous Information (text): Country of Origin, Substantiated Claims, Trademark Clause, Carrier
Extract other information mentioned as well , Give result in json format. In case a key/field has no value respond with "NA" """