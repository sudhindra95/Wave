import csv
from flask import Flask, request, jsonify
from models import db, FileData, EmployeeData
from datetime import datetime
import calendar
from utils import formatAmountPaid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()


@app.route('/upload', methods=['POST'])
def upload_file():

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    if file and file.filename.endswith('.csv'):
        # Check if file with the same name already exists
        existing_file = FileData.query.filter_by(filename=file.filename).first()
        if existing_file:
            return jsonify({'message': 'File already exists'}), 409

        # Save the file to the database
        new_file = FileData(filename=file.filename, data=file.read())
        db.session.add(new_file)
        db.session.commit()

        file.stream.seek(0)  # Ensure you're at the start of the file
        csv_reader = csv.reader(file.stream.read().decode('utf-8').splitlines())

        header=next(csv_reader)

        for row in csv_reader:
            employee_row = EmployeeData(date=row[0], hours_worked=row[1], employee_id=row[2], job_group=row[3])
            db.session.add(employee_row)


        db.session.commit()

        return jsonify({'message': 'File successfully uploaded and saved'}), 200
    else:
        return jsonify({'error': 'Only CSV files are allowed'}), 400




@app.route('/view/<filename>', methods=['GET'])
def view_file(filename):
    file_data = FileData.query.filter_by(filename=filename).first()
    if not file_data:
        return jsonify({'error': 'File not found'}), 404

    # file_content = io.BytesIO(file_data.data)
    # df = pd.read_csv(file_content)
    # return jsonify(df.to_dict(orient='records'))
    return jsonify({'message': 'File is present'}), 200



@app.route('/getData', methods=['GET'])
def retrieve_report():
    # Query all rows from the CSVData table
    csv_data = EmployeeData.query.all()

    # Convert the data to a list of dictionaries
    result = []
    for row in csv_data:
        row_dict = {
            'id': row.id,
            'date': row.date,
            'hours worked': row.hours_worked,
            'employee id': row.employee_id,
            'job group': row.job_group
        }
        result.append(row_dict)

    return jsonify(result), 200




@app.route('/payroll_report', methods=['GET'])
def get_payroll_report():
    def get_pay_period(date):
        date = datetime.strptime(date, '%d/%m/%Y')  # Parse the date string to a datetime object
        if date.day <= 15:
            start_date = date.replace(day=1)
            end_date = date.replace(day=15)
        else:
            start_date = date.replace(day=16)
            last_day = calendar.monthrange(date.year, date.month)[1]
            end_date = date.replace(day=last_day)

        return {'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')}

    # Hourly rates for job groups
    hourly_rates = {'A': 20.00, 'B': 30.00}

    # Query all work data and organize it by employee and pay period
    work_data = EmployeeData.query.all()
    payroll_data = {}

    for entry in work_data:
        employee_id = entry.employee_id
        pay_period = get_pay_period(entry.date)
        pay_period_key = (employee_id, pay_period['startDate'], pay_period['endDate'])

        if pay_period_key not in payroll_data:
            payroll_data[pay_period_key] = {
                'employeeId': employee_id,
                'payPeriod': pay_period,
                'amountPaid': 0.0
            }

        payroll_data[pay_period_key]['amountPaid'] += entry.hours_worked * hourly_rates[entry.job_group]


    formatAmountPaid(payroll_data)



    # Convert the payroll data to the desired JSON format
    payroll_report = {
        'payrollReport': {
            'employeeReports': sorted(payroll_data.values(), key=lambda x: (x['employeeId'], x['payPeriod']['startDate']))
        }
    }

    return jsonify(payroll_report), 200






if __name__ == '__main__':
    app.run(debug=True)