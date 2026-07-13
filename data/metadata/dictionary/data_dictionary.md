# Data Dictionary

## customers_dataset
- customer_id: Primary Key (str)
- customer_unique_id: Identifier (str)
- customer_zip_code_prefix: Postal Code (int64)
- customer_city: City (str)
- customer_state: State (str)

## geolocation_dataset
- geolocation_zip_code_prefix: Postal Code (int64)
- geolocation_lat: Latitude (float64)
- geolocation_lng: Longitude (float64)
- geolocation_city: City (str)
- geolocation_state: State (str)

## order_items_dataset
- order_id: Foreign Key (str)
- order_item_id: Identifier (int64)
- product_id: Foreign Key (str)
- seller_id: Foreign Key (str)
- shipping_limit_date: Datetime (datetime64[us])
- price: Currency (float64)
- freight_value: Currency (float64)

## order_payments_dataset
- order_id: Foreign Key (str)
- payment_sequential: Currency (int64)
- payment_type: Currency (str)
- payment_installments: Currency (int64)
- payment_value: Currency (float64)

## order_reviews_dataset
- review_id: Primary Key (str)
- order_id: Primary Key (str)
- review_score: Rating (int64)
- review_creation_date: Datetime (datetime64[us])
- review_answer_timestamp: Primary Key (datetime64[us])

## orders_dataset
- order_id: Primary Key (str)
- customer_id: Primary Key (str)
- order_status: Category (str)
- order_purchase_timestamp: Primary Key (datetime64[us])
- order_approved_at: Datetime (datetime64[us])
- order_delivered_carrier_date: Datetime (datetime64[us])
- order_delivered_customer_date: Datetime (datetime64[us])
- order_estimated_delivery_date: Datetime (datetime64[us])

## product_category_name_translati
- Column1: Primary Key (str)
- Column2: Primary Key (str)

## products_dataset
- product_id: Primary Key (str)
- product_category_name: Category (str)
- product_name_lenght: Decimal (float64)
- product_description_lenght: Decimal (float64)
- product_photos_qty: Decimal (float64)
- product_weight_g: Weight (float64)
- product_length_cm: Dimension (float64)
- product_height_cm: Dimension (float64)
- product_width_cm: Dimension (float64)

## sellers_dataset
- seller_id: Primary Key (str)
- seller_zip_code_prefix: Postal Code (int64)
- seller_city: City (str)
- seller_state: State (str)
