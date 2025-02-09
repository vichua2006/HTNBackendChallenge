import requests

badge_code = "to-send-here-north"
new_code = "hey-north-food-good"
# url = f"http://localhost:5000/users/{badge_code}"
url = f"http://localhost:5000/scans/{new_code}"

response = requests.put(
    url,
    json={
        "badge_code": badge_code,
    },
    # json={
    #     "activity_name": "North Food",
    #     "activity_category": "Food",
    # }
)

print(response.json())
