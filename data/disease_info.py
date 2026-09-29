DISEASE_INFO = {

    "Torticollis": {

        "description":
            "A condition associated with abnormal twisting or positioning of the neck.",

        "possible_causes": [
            "Neurological problems",
            "Nutritional deficiencies",
            "Infectious diseases",
            "Injury"
        ],

        "common_signs": [
            "Abnormal neck position",
            "Difficulty maintaining normal posture",
            "Difficulty feeding or drinking"
        ],

        "prevention": [
            "Maintain good farm hygiene",
            "Provide balanced nutrition",
            "Provide clean drinking water",
            "Monitor birds regularly",
            "Separate visibly affected birds and seek veterinary advice"
        ],

        "management":
            "Monitor the affected bird and investigate the underlying cause with a poultry veterinarian."
    }

}


def get_disease_info(class_name):

    return DISEASE_INFO.get(
        class_name,
        {
            "description": "Information not available.",
            "possible_causes": [],
            "common_signs": [],
            "prevention": [],
            "management": "Consult a poultry veterinarian."
        }
    )