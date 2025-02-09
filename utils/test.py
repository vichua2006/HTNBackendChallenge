import requests

badge_code = "to-send-here-north"
new_code = "hey-north-food-good"
# url = f"http://localhost:5000/users/{badge_code}"
url = f"http://localhost:5000/scans/{new_code}"

response = requests.put(
    url,
    # json={
    #     "name": "Foo Doe",
    #     "email": "jd@example.com",
    #     "phone": "123-456-7890",
    #     "badge_code": new_code,
    # },

    json={
        "activity_name": "North Food",
    }
)

print(response.json())
