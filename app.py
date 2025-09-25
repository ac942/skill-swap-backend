from flask import Flask, request, jsonify
import boto3
import uuid

app = Flask(__name__)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('Users')

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Generate unique userId
    user_id = str(uuid.uuid4())

    item = {
        "userId": user_id,
        "name": data.get("name"),
        "skills_known": data.get("skills_known", []),
        "skills_wanted": data.get("skills_wanted", []),
        "location": data.get("location"),
        "availability": data.get("availability")
    }

    users_table.put_item(Item=item)
    return jsonify({"message": "User registered successfully", "userId": user_id})
@app.route('/users', methods=['GET'])
def get_users():
    try:
        response = users_table.scan()
        users = response.get('Items', [])
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/matches', methods=['GET'])
def get_matches():
    user_id = request.args.get('userId')
    
    if not user_id:
        return jsonify({'error': 'Missing userId'}), 400

    response = users_table.scan()
    all_users = response.get('Items', [])

    current_user = next((user for user in all_users if user['userId'] == user_id), None)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404

    matches = []

    for other_user in all_users:
        if other_user['userId'] == user_id:
            continue

        skills_they_can_teach = set(other_user['skills_known']).intersection(current_user['skills_wanted'])
        skills_you_can_teach = set(current_user['skills_known']).intersection(other_user['skills_wanted'])
        availability_match = other_user['availability'] == current_user['availability']

        if skills_they_can_teach and skills_you_can_teach:
            match_score = len(skills_they_can_teach) + len(skills_you_can_teach)
            if availability_match:
                match_score += 1

            matches.append({
                'name': other_user['name'],
                'location': other_user['location'],
                'userId': other_user['userId'],
                'skills_they_can_teach_you': list(skills_they_can_teach),
                'skills_you_can_teach_them': list(skills_you_can_teach),
                'availability': other_user['availability'],
                'score': match_score
            })

    sorted_matches = sorted(matches, key=lambda x: x['score'], reverse=True)
    return jsonify(sorted_matches), 200


# ⚠️ Keep this last part at the end
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
