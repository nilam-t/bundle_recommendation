
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def print_Description_of_StockCode(data, stock_code):
  description = []
  if type(stock_code) != list:
    #print()
    description.append(data[data['StockCode'] == stock_code][['Description']].values[0].tolist()[0])
  else:
    for stc in stock_code:
      description.append(data[data['StockCode'] == stc][['Description']].values[0].tolist()[0])
  return description


### rewrite this function
def obtain_recommendations(stock_code, rules, recommendation_count):
  #print(f'Here stock_code {stock_code}')
  #print(rules.head())
  sorted_rules = rules.sort_values('lift', ascending=False, ignore_index=True)
  product_ids, product_lift = [], []
  for i, product in sorted_rules['antecedents'].items():
    for j in list(product):
      if j == stock_code:
        for pr_id in list(sorted_rules.iloc[i]['consequents']):
          product_ids.append(pr_id)
          product_lift.append(sorted_rules.iloc[i]['lift'])

  pr_id_lift = pd.DataFrame(list(zip(product_ids, product_lift)), columns = ['ID', 'Lift'])
  pr_id_lift = pr_id_lift.groupby('ID')
  pr_id_lift = pr_id_lift.agg({"Lift": "max"}).reset_index()
  pr_id_lift = pr_id_lift.sort_values('Lift', ascending=False, ignore_index=True)
  recommended_products = list(pr_id_lift['ID'])
  #print(recommended_products)
  return recommended_products[:recommendation_count]

def print_recommendations(stock_code, data, rules, recommendation_count):
  product_name = print_Description_of_StockCode(data, stock_code)
  recommended_stock_codes = obtain_recommendations(stock_code, rules, recommendation_count)
  print(recommended_stock_codes)
  recommended_product_description = print_Description_of_StockCode(data, recommended_stock_codes)
  #print(f'Product ID : {stock_code} \nProduct Name: {product_name}')
  #print(f'Recommended-product IDs : {recommended_stock_codes} \nRecommended-product Names: {recommended_product_description}')

  return product_name, recommended_product_description

#data_pkl = pd.read_pickle("filtered_dt.pkl")
#rules_pkl = pd.read_pickle("rules.pkl")

#print(data_pkl.shape)
#print(rules_pkl.shape)

#rec_id = print_recommendations('23235',data_pkl,rules_pkl,5)
#rec_id = print_recommendations('21987',data_pkl,rules_pkl,5)