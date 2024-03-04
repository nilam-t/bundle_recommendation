import logging, argparse, zipfile, mlxtend
import sys
from mlxtend.frequent_patterns import association_rules, fpgrowth

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


params = {}
parser = argparse.ArgumentParser(description='Parameter Parser', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--productID',      default='21987', type=str, required=True,  help='Enter product-ID')
parser.add_argument('--b',      default=1, type=int,   help='Number of bundles to output')
parser.add_argument('--logfile',        default='info.log',       help='save recommendations in this file')
pargs = parser.parse_args()
params.update(vars(pargs))

log = logging.getLogger()
logging.basicConfig(filename=params['logfile'], filemode='w')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)
log.info(params)

def clean_dataset(data):
  """ This function cleans the transaction dataset
  :param data: transaction dataset
  :return: cleaned dataset
  """
  # remove rows with NA values in the dataset
  data.dropna(inplace=True)
  # remove cancelled transactions
  data = data[~data['InvoiceNo'].str.contains('C')]
  # remove StockCodes associated with shipping and other charges
  data = data[~data['StockCode'].str.contains('POST|M|DOT|BANK CHARGES|C2|PADS')]
  # Only consider valid purchases
  data = data[data['UnitPrice'] > 0.0]
  return data

def print_Description_of_StockCode(data, stock_code):
  """ Return the product Description of the provided stockCode/product-id
  :param data: transaction data containing Description and stockCode
  :param stock_code: product-ID or list of product-IDs for which users want the Description. a 5-digit integral number uniquely assigned to each distinct product
  :return: Description o
  """
  description = []
  if type(stock_code) != list:
    #print()
    description.append(data[data['StockCode'] == stock_code][['Description']].values[0].tolist()[0])
  else:
    for stc in stock_code:
      description.append(data[data['StockCode'] == stc][['Description']].values[0].tolist()[0])

  return description

def obtain_StockCode_prices(data, rec_stock_code, stock_code):
  price_list = []
  price_list.append(data[data['StockCode'] == stock_code][['UnitPrice']].values[0].tolist()[0])
  if type(rec_stock_code) != list:
    price_list.append(data[data['StockCode'] == rec_stock_code][['UnitPrice']].values[0].tolist()[0])
  else:
    for stc in rec_stock_code:
      price_list.append(data[data['StockCode'] == stc][['UnitPrice']].values[0].tolist()[0])

  return price_list


### rewrite this function
def obtain_recommendations(stock_code, rules, recommendation_count):
  sorted_rules = rules.sort_values('lift', ascending=False, ignore_index=True)
  product_ids, product_lift = [], []
  recommended_products = []
  for i, product in sorted_rules['antecedents'].items():
    if (len(list(product)) == 1) & (list(product)[0] == stock_code):
      # print(list(sorted_rules.iloc[i]['consequents']))
      recommended_products.append(list(sorted_rules.iloc[i]['consequents']))
      #for conseq in list(sorted_rules.iloc[i]['consequents']):
      #  recommended_products.append(conseq)
  # print(recommended_products)
  return recommended_products[:recommendation_count]

def print_recommendations(stock_code, data, rules, recommendation_count):
  product_name = print_Description_of_StockCode(data, stock_code)
  recommended_stock_codes = obtain_recommendations(stock_code, rules, recommendation_count)
  # print(recommended_stock_codes)
  log.info(f'Product ID : {stock_code} \nProduct Name: {product_name}')
  for cnt in range(recommendation_count):
    recommended_product_description = print_Description_of_StockCode(data, recommended_stock_codes[cnt])
    bundle_price_list = obtain_StockCode_prices(data, recommended_stock_codes[cnt], stock_code)
    # print(bundle_price_list)
    log.info(f'Bundle No: {cnt+1} Recommended-product IDs : {recommended_stock_codes[cnt]} '
          f'\nRecommended-product Names: {recommended_product_description}')
    log.info('Bundle Total Price (in Sterling): {:.2f}\n'.format(sum(bundle_price_list)))

# extract contents of the zip file
zip_ref = zipfile.ZipFile('ecommerce-data.zip', 'r')
#if not os.path.exists('/data/'):
#  os.makedirs('/data/')
zip_ref.extractall('data')
zip_ref.close()
log.info("Data extracted")

# load the csv data file
dt = pd.read_csv('data/data.csv', encoding='unicode_escape', dtype={'CustomerID':str, 'InvoiceNo':str}, parse_dates=['InvoiceDate'])
log.info("Data Loaded")

# clean the dataset
filtered_dt = clean_dataset(dt)
if (params['productID'] not in filtered_dt['StockCode'].unique()):
  sys.exit("Please enter valid product ID")

# Transform the data to be used by GP-Growth algorithm. The given data is grouped by "InvoiceNo" and "StockCode" and aggregated by "Quantity".
# If a StockCode is present in a given "InvoiceNo" then that entry is filled with 1, otherwise it is 0
transformed_dt = filtered_dt.groupby(['InvoiceNo','StockCode'])['Quantity'].sum().unstack().fillna(0).applymap(lambda x: 1 if x>0 else 0)
log.info("Data Preprocessing done")

# Apply GP-Growth algorithm on the transformed data to obtain frequent itemsets.
# The minimum support is set at 0.002 i.e. an itemset is considered frequent if it appears in more than or equal to 0.2% transactions
frequent_itemsets = fpgrowth(transformed_dt, min_support=0.002, use_colnames=True)
log.info("Frequent itemsets are generated")
# Association rules are generated using "support" metrics
rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.002)
log.info("Association rules are obtained")

print_recommendations(params['productID'],filtered_dt,rules,params['b'])