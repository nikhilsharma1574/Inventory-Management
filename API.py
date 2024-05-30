from flask import Flask, render_template, redirect, jsonify, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.secret_key = "Shubhankar" #Used for encrypting sessions


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1001@localhost/NqtProjDB'
db = SQLAlchemy(app)

class User(db.Model):
    UID = db.Column(db.Integer, primary_key=True)
    isAdmin = db.Column(db.Boolean)
    FullName = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    Password = db.Column(db.String(255))

    assigned_items = db.relationship('Items', backref='user', lazy=True)

    def serialize(self):
        return {
            'UID': self.UID,
            'isAdmin': self.isAdmin,
            'FullName': self.FullName,
            'Email': self.Email
        }

class Items(db.Model):
    SerialNumber = db.Column(db.String(50), primary_key=True)
    ItemName = db.Column(db.String(255))
    Quantity = db.Column(db.Integer)
    Category = db.Column(db.String(100))
    BillNumber = db.Column(db.String(50))
    DateOfPurchase = db.Column(db.Date)
    Warranty = db.Column(db.String(100))
    AssignedTo = db.Column(db.Integer, db.ForeignKey('user.UID'))  # Define foreign key
    
    def serialize(self):
        return {
            'SerialNumber': self.SerialNumber,
            'ItemName': self.ItemName,
            'Quantity': self.Quantity,
            'Category': self.Category,
            'BillNumber': self.BillNumber,
            'DateOfPurchase': self.DateOfPurchase,
            'Warranty': self.Warranty,
            'AssignedTo': self.AssignedTo
        }
    

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        #check if user exsists
        user = User.query.filter_by(Email=email, Password=password).first()

        if user:
            session["user_id"] = user.UID
            if user.isAdmin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('employee'))
        else:
            return 'Invalid credentials'
    else:
        user_id = session.get('user_id')
        if "user_id" in session:
            user = User.query.get(user_id)
            if user.isAdmin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('employee'))
        return render_template('index.html') 

@app.route('/logout')
def logout():
    session.pop("user_id",None)
    flash("Logged Out Succesfully","info") #"info category hai" , warning and error also
    return redirect(url_for("login"))

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@app.route('/admin', methods=['GET','POST'])
def admin():
    user_id = session.get('user_id')
    if user_id:
        this_user = User.query.get(user_id)
        if this_user.isAdmin:
            filter_type = request.args.get('filter', 'all')

            items = []
            users = User.query.all()
            categories = {}

            if filter_type == 'all_items':
                items = Items.query.all()
            elif filter_type == 'assigned':
                items = Items.query.filter(Items.AssignedTo.isnot(None)).all()
            elif filter_type == 'unassigned':
                items = Items.query.filter(Items.AssignedTo.is_(None)).all()
            elif filter_type == 'category':
                items = Items.query.all()
                for item in items:
                    if item.Category not in categories:
                        categories[item.Category] = []
                    categories[item.Category].append(item)
            else:
                items = Items.query.all()

            return render_template('admin.html', user=this_user, items=items, users=users, categories=categories, filter_type=filter_type)
        else:
            return "Not Admin"
    else:
        return redirect(url_for('/'))


    
@app.route('/employee')
def employee():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('employee.html', user=user)
    else:
        return redirect(url_for('/'))

@app.route('/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'GET':
        users = User.query.all()
    elif request.method == 'POST':
        print("Users Post Succesfull")
        isAdmin_str = request.form.get('isAdmin', 'off')  # Default value if checkbox is unchecked
        isAdmin = 0 if isAdmin_str == 'off' else 1
        fullName = request.form['fullName']
        email = request.form['email']
        password = request.form['password']

        new_user = User(isAdmin=isAdmin, FullName=fullName, Email=email, Password=password)
        db.session.add(new_user)
        db.session.commit()
    
        users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/items', methods=['GET', 'POST'])
def handle_items():
    if request.method == 'POST':
        print("Items Post Successful")
        serialNumber = request.form['serialNumber']
        itemName = request.form['itemName']
        quantity = request.form['quantity']
        category = request.form['category']
        billNumber = request.form['billNumber']
        dateOfPurchase = request.form['dateOfPurchase']
        warranty = request.form['warranty']
        assignedTo = request.form['assignedTo']

        new_item = Items(SerialNumber=serialNumber, ItemName=itemName, Quantity=quantity, Category=category,
                         BillNumber=billNumber, DateOfPurchase=dateOfPurchase, Warranty=warranty, AssignedTo=assignedTo)
        db.session.add(new_item)
        db.session.commit()

    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        print("Items Post Successful")
        serialNumber = request.form['serialNumber']
        itemName = request.form['itemName']
        quantity = request.form['quantity']
        category = request.form['category']
        billNumber = request.form['billNumber']
        dateOfPurchase = request.form['dateOfPurchase']
        warranty = request.form['warranty']
        assignedTo = request.form['assignedTo']

        new_item = Items(SerialNumber=serialNumber, ItemName=itemName, Quantity=quantity, Category=category,
                         BillNumber=billNumber, DateOfPurchase=dateOfPurchase, Warranty=warranty, AssignedTo=assignedTo)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('add_item.html')


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        print("Users Post Succesfull")
        isAdmin_str = request.form.get('isAdmin', 'off')  # Default value if checkbox is unchecked
        isAdmin = 0 if isAdmin_str == 'off' else 1
        fullName = request.form['fullName']
        email = request.form['email']
        password = request.form['password']

        new_user = User(isAdmin=isAdmin, FullName=fullName, Email=email, Password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('add_user.html')



@app.route('/delete-item', methods=['POST'])
def delete_item():
    serialNumber = request.form['serialNumber']
    item_to_delete = Items.query.filter_by(SerialNumber=serialNumber).first()
    if item_to_delete:
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect('/admin')  # Redirect to the main page after deleting
    else:
        return 'Item not found', 404
    
    
@app.route('/delete-user', methods=['POST'])
def delete_user():
    uid = request.form['uid']
    user_to_delete = User.query.filter_by(UID=uid).first()
    if user_to_delete:
        #Show Popup to ask confirm delete if yes then delete
        db.session.delete(user_to_delete)
        db.session.commit()

        return redirect(url_for('admin'))  # Redirect to the main page after deleting
    else:
        return '<alert>User not found</alert>', 404


@app.route('/assign-item', methods=['POST'])
def assign_item():
    if request.method == 'POST':
        serialNumber = request.form['serialNumber']
        assignedTo = request.form['assignedTo']
        
        # Update the assignedTo field in the database for the item with the given serial number
        item = Items.query.filter_by(SerialNumber=serialNumber).first()
        if item:
            item.AssignedTo = assignedTo
            db.session.commit()
            # Redirect back to the admin page after assigning the item
            return redirect(url_for('admin'))
        else:
            # Handle case where item with the given serial number does not exist
            return 'Item not found', 404

@app.route('/unassign-item', methods=['POST'])
def unassign_item():
    serial_number = request.form['serialNumber']

    items = Items.query.filter_by(SerialNumber=serial_number).first()
    if items:
        items.AssignedTo = None
        db.session.commit()
        return redirect(url_for("admin"))
    else:
        return 'Item not found', 404

if __name__ == '__main__':
    app.run(debug=True)
