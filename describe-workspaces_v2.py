# Step 1: Run the describe-workspace-bundles command
aws workspaces describe-workspace-bundles --output json > output.json

# Step 2: Convert JSON to CSV using Python
python - <<EOF
import json
import csv

# Load the JSON data
with open('output.json') as json_file:
    data = json.load(json_file)

# Open a CSV file for writing
with open('output.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write the header
    header = ["BundleId", "Name", "Owner", "Description"]
    csv_writer.writerow(header)

    # Write the data rows
    for bundle in data['Bundles']:
        row = [
            bundle.get('BundleId', ''),
            bundle.get('Name', ''),
            bundle.get('Owner', ''),
            bundle.get('Description', '')
        ]
        csv_writer.writerow(row)
EOF

# Step 3: Upload the CSV file to S3
aws s3 cp output.csv s3://your-bucket-name/path/to/output.csv
