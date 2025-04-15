import json


def lowercase_json(data):
    if isinstance(data, dict):
        return {key.lower(): lowercase_json(value) if isinstance(key, str) else lowercase_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [lowercase_json(item) for item in data]
    elif isinstance(data, str):
        return data.lower()
    else:
        return data
    
def regex_search_irs(var):
    print(var)
    text = str(var)
    start_index = text.find('{')

    # Find the ending index of the last }
    end_index = text.rfind('}')

    # Extract the desired content
    clean_text = text[start_index:end_index + 1]
    data = json.loads(clean_text)
    print(data)
    # data = lowercase_json(json.loads(var)) 
    # data = lowercase_json(json.loads(var))
    print(data["document_info"])
    name_of_business = data["document_info"][0]["business_name"]
    tax_id =  data["document_info"][0]["tax_id"]
    employer_identification_number = data["document_info"][0]["employer_identification_number"]
    return name_of_business, tax_id, employer_identification_number
    
def regex_search_pli(var):
    print(var) 
    text = str(var)
    start_index = text.find('{')

    # Find the ending index of the last }
    end_index = text.rfind('}')

    # Extract the desired content
    clean_text = text[start_index:end_index + 1]
    
    data = json.loads(clean_text)
    # Load the JSON data
    # data = lowercase_json(json.loads(var)) 
    board_name = data["document_info"][0]["board_name"]
    line_of_business = data["document_info"][0]["line_of_business"]
    license_number = data["document_info"][0]["license_number"]
    issue_date = data["document_info"][0]["issue_date"]
    issued_to=data["document_info"][0]["issued_to"]
    return board_name, line_of_business, license_number, issue_date, issued_to


def regex_search_bankLetter(var):
    # Find the starting index of the first {
    text = str(var)
    start_index = text.find('{')

    # Find the ending index of the last }
    end_index = text.rfind('}')

    # Extract the desired content
    clean_text = text[start_index:end_index + 1]
    
    data = lowercase_json(json.loads(clean_text)) 
    print("data from regexxxx")
    print(clean_text)
    account_name = data["document_info"][0]["account_name"]
    account_number = data["document_info"][0]["account_number"]
    routing_number = data["document_info"][0]["routing_number"]
    aba = data["document_info"][0]["aba"]
    return account_name,account_number,routing_number,aba

def regex_search_clia(var):
    text = str(var)
    start_index = text.find('{')

    # Find the ending index of the last }
    end_index = text.rfind('}')

    # Extract the desired content
    clean_text = text[start_index:end_index + 1]
    
    data = lowercase_json(json.loads(clean_text)) 
    print("data from regexxxx")
    print(clean_text)
    clia_id = (data["document_info"][0]["clia_id"] or data["document_info"][0]["CLIA_ID"] )
    start_date = data["document_info"][0]["start_date"]
    expiration_date = data["document_info"][0]["expiration_date"]
    business_name = data["document_info"][0]["business_name"]
    certification_type = data["document_info"][0]["certification_type"]
    return clia_id, start_date, expiration_date ,business_name , certification_type

def regex_search_fac_license(var):
    text = str(var)
    print(var)
    start_index = text.find('{')

    # Find the ending index of the last }
    end_index = text.rfind('}')

    # Extract the desired content
    clean_text = text[start_index:end_index + 1]
    
    data = lowercase_json(json.loads(clean_text)) 
    print("data from regexxxx")
    print(data)
    issuing_board_name = data["document_info"][0]["issuing_board_name"]
    business_name = data["document_info"][0]["business_name"]
    license_number = data["document_info"][0]["license_number"]
    issue_date = data["document_info"][0]["issue_date"]
    expiration_date = data["document_info"][0]["expiration_date"]
    license_type = data["document_info"][0]["license_type"]
    return issuing_board_name, business_name, license_number, issue_date , expiration_date , license_type

def regex_search_liability_certificate(var):
    text = str(var)
    print(var)
    start_index = text.find('{')

    # Find the ending index of the last }
    end_index = text.rfind('}')

    # Extract the desired content
    clean_text = text[start_index:end_index + 1]
    
    data = lowercase_json(json.loads(clean_text)) 
    print("data from regexxxx")
    print(clean_text)
    insured_name = data["document_info"][0]["insured_name"]
    policy_number = data["document_info"][0]["policy_number"]
    policy_effective_date = data["document_info"][0]["policy_effective_date"]
    policy_expiration_date = data["document_info"][0]["policy_expiration_date"]
    coverage_limit = data["document_info"][0]["coverage_limit"]
    per_claim_limit = data["document_info"][0]["per_claim_limit"]
    aggregate = data["document_info"][0]["aggregate"]
    policy_type = data["document_info"][0]["policy_type"]
    return insured_name, policy_number, policy_effective_date, policy_expiration_date, coverage_limit,per_claim_limit, aggregate, policy_type
    
