import pickle
import os
import pandas as pd

# Current directory path
dir_path = os.path.dirname(os.path.abspath(__file__))

# Load pkl files
file_path = os.path.join(dir_path, 'Cleaned_Bengaluru_House_Data.pkl')
with open(file_path, 'rb') as file:
    property_data = pickle.load(file)
file_path = os.path.join(dir_path, 'RidgeModel.pkl')
with open(file_path, 'rb') as file:
    pipe = pickle.load(file)

def format_inr(amount):
    amount_str = f"{amount:,.2f}"
    if '.' in amount_str:
        integer_part, fractional_part = amount_str.split('.')
    else:
        integer_part, fractional_part = amount_str, ''

    integer_part = integer_part.replace(",", "")
    integer_part = integer_part[::-1]
    inr_formatted = integer_part[:3]

    for i in range(3, len(integer_part), 2):
        inr_formatted += ',' + integer_part[i:i + 2]

    inr_formatted = inr_formatted[::-1]
    formatted_inr = f"₹{inr_formatted}.{fractional_part}"

    # Calculate amount in crores and lakhs
    amount_int = int(amount)
    if amount >= 1e7:
        amount_in_cr = amount / 1e7
        shorthand_formatted = f"₹{amount_in_cr:,.2f} Cr"
    else:
        amount_in_lakh = amount / 1e5
        shorthand_formatted = f"₹{amount_in_lakh:,.2f} Lakh"

    return formatted_inr, shorthand_formatted

def get_requirements():
    locations = property_data['location'].unique().tolist()
    bhks = sorted(property_data['bhk'].unique().tolist())
    baths = {bath: int(bath) for bath in sorted(property_data['bath'].unique().tolist())}
    return {
        'locations': locations,
        'bhks': bhks,
        'baths': baths,
    }

def get_predicted_price(location, total_sqft, bath, bhk):
    df = pd.DataFrame(
        [[location, total_sqft, bath, bhk]],
        columns=['location', 'total_sqft', 'bath', 'bhk']
    )
    price = pipe.predict(df)[0] * 100000
    return format_inr(price)
