from services.result_analyzer import generate_chart_spec


rows = [
    {"price": "2099.00", "total_quantity_ordered": 199},
    {"price": "1499.00", "total_quantity_ordered": 196},
    {"price": "1399.00", "total_quantity_ordered": 202},
]


chart = generate_chart_spec(rows)

print(chart)