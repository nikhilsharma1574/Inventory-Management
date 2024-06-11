from flask import Flask, render_template, redirect, jsonify, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

import logging
import re
app = Flask(__name__)
app.secret_key = "Shubhankar" #Used for encrypting sessions

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1001@localhost/NqtProjDB'
db = SQLAlchemy(app)
# Setup logging
logging.basicConfig(filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def log_message(message):
    with open('apps.log', 'a') as log_file:
        log_file.write(f"{message}\n")

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
    SerialNumber = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ItemName = db.Column(db.String(100), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    Category = db.Column(db.String(100), nullable=False)
    BillNumber = db.Column(db.String(20), nullable=False)
    DateOfPurchase = db.Column(db.String(20), nullable=False)
    Warranty = db.Column(db.String(50), nullable=False)
    AssignedTo = db.Column(db.Integer, db.ForeignKey('user.UID'), nullable=True, default=None)

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
        email_prefix  = request.form['email']
        password = request.form['password']
        logger.info(f"Login attempt with email: {email_prefix}@nucleusteq.com")
        log_message(f"Login attempt with email: {email_prefix}@nucleusteq.com")
        # Append the email suffix
        email = email_prefix + "@nqt.com"
        #check if user exsists
        user = User.query.filter_by(Email=email, Password=password).first()

        if user:
            session["user_id"] = user.UID
            if user.isAdmin:
                flash('Succesfully Logged In','success')
                return redirect(url_for('admin'))
            else:
                flash('Succesfully Logged In','success')
                return redirect(url_for('employee'))
        else:
            flash('Invalid credentials','error')
            return redirect(url_for('login'))
            
    else:
        user_id = session.get('user_id')
        if "user_id" in session:
            user = User.query.get(user_id)
            if user.isAdmin:
                flash('Welcome Admin','success')
                return redirect(url_for('admin'))
            else:
                flash('Welcome Employee','success')
                return redirect(url_for('employee'))
        return render_template('index.html') 

@app.route('/logout')
def logout():
    log_message(f"Logged Out")
    logger.info(f"Logged out")
    session.pop("user_id",None)
    flash("Logged Out Succesfully","info") #"info category hai" , warning and error also
    return redirect(url_for("login"))

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    logger.info(f"Profile Page for UID : {user_id}")
    log_message(f"Profile Page for UID : {user_id}")
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
                logger.info(f"All Itemsview")
                log_message(f"All Items view")
                items = Items.query.all()
            elif filter_type == 'assigned':
                logger.info(f"Assigned Items Filter")
                log_message(f"Assigned Items Filter")
                items = Items.query.filter(Items.AssignedTo.isnot(None)).all()
            elif filter_type == 'unassigned':
                logger.info(f"Unssigned Items Filter")
                log_message(f"Unssigned Items Filter")
                items = Items.query.filter(Items.AssignedTo.is_(None)).all()
            elif filter_type == 'category':
                logger.info(f"Category Group Filter")
                log_message(f"Category Group Filter")
                items = Items.query.all()
                for item in items:
                    if item.Category not in categories:
                        categories[item.Category] = []
                    categories[item.Category].append(item)
            else:
                items = Items.query.all()

            return render_template('admin.html', user=this_user, items=items, users=users, categories=categories, filter_type=filter_type)
        else:
            logger.info(f"Employee Denied Admin Page Access")
            log_message(f"Employee Denied Admin Page Access")
            return "Not Admin"
    else:
        return redirect(url_for('/'))


    
@app.route('/employee')
def employee():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        logger.info(f"Employee Loggedin")
        log_message(f"Employee Loggedin")
        return render_template('employee.html', user=user)
    else:
        log_message(f"No User Exists")
        return redirect(url_for('/'))

@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    users = User.query.all()
    if request.method == 'POST':
        itemName = request.form['itemName']
        quantity = request.form['quantity']
        category = request.form['category']
        billNumber = request.form['billNumber']
        dateOfPurchase = request.form['dateOfPurchase']
        warranty = request.form['warranty']

        assigned_to = request.form.get('assignedTo')
        if assigned_to == '':
            assigned_to = None
        
        existing_item = Items.query.filter_by(AssignedTo=assigned_to, Category=category).first()
        if existing_item:
            flash('User already has an item of this category assigned', 'error')
            return redirect(request.referrer or url_for('add_item'))

        new_item = Items(ItemName=itemName, Quantity=quantity, Category=category,
                         BillNumber=billNumber, DateOfPurchase=dateOfPurchase, Warranty=warranty, AssignedTo=assigned_to)
        db.session.add(new_item)
        db.session.commit()
        logger.info(f"New Item Added")
        log_message(f"New Item Added")
        return redirect(url_for('admin'))

    return render_template('add_item.html', users=users)


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    user = None
    if "user_id" in session:
        user = User.query.get(session["user_id"])

    if request.method == 'POST':
        isAdmin_str = request.form.get('isAdmin', 'off')  # Default value if checkbox is unchecked
        isAdmin = 0 if isAdmin_str == 'off' else 1
        fullName = request.form['fullName']
        email_prefix = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        # Append the email suffix
        email = email_prefix + "@nqt.com"

        # Server-side validation for email and password
        if not email_prefix.isalnum() or not email_prefix.islower():
            flash('Invalid email prefix. Only lowercase letters and numbers are allowed.', 'danger')
            return redirect(url_for('add_user'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('add_user'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('add_user'))

        new_user = User(isAdmin=isAdmin, FullName=fullName, Email=email, Password=password)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New User Added")
        log_message(f"New User Added")

        session["user_id"] = new_user.UID

        flash('User added successfully!', 'success')
        if new_user.isAdmin:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('employee'))

    return render_template('add_user.html', user=user)





@app.route('/delete-item', methods=['POST'])
def delete_item():
    serialNumber = request.form['serialNumber']
    item_to_delete = Items.query.filter_by(SerialNumber=serialNumber).first()
    if item_to_delete:
        db.session.delete(item_to_delete)
        db.session.commit()
        logger.info(f"Item Deleted")
        log_message(f"Item Deleted")
        flash('Item Deleted', 'success')
        return redirect(request.referrer or url_for('admin'))  # Redirect to the main page after deleting
    else:
        flash('Item not found', 'error')
        return 'Item not found', 404
    
    
@app.route('/delete-user', methods=['POST'])
def delete_user():
    uid = request.form['uid']
    user_to_delete = User.query.filter_by(UID=uid).first()
    if user_to_delete:
        #Show Popup to ask confirm delete if yes then delete
        db.session.delete(user_to_delete)
        db.session.commit()

        logger.info(f"User Deleted ")
        log_message(f"User Deleted ")
        flash('User Deleted', 'success')
        return redirect(request.referrer or url_for('admin')) # Redirect to the main page after deleting
    else:
        flash('User not found', 'error')
        return '<alert>User not found</alert>', 404




@app.route('/assign-item', methods=['POST'])
def assign_item():
    serialNumber = request.form['serialNumber']
    assignedTo = request.form['assignedTo']

    # Check if the item exists
    item = Items.query.filter_by(SerialNumber=serialNumber).first()
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('admin'))

    # Check if the user already has an item of the same category assigned
    existing_item = Items.query.filter_by(AssignedTo=assignedTo, Category=item.Category).first()
    if existing_item:
        flash('User already has an item of this category assigned', 'error')
        return redirect(url_for('admin'))

    # Assign the item to the user
    item.AssignedTo = assignedTo
    db.session.commit()
    logger.info(f"Item {serialNumber} Assigned to User {assignedTo}")
    log_message(f"Item {serialNumber} Assigned to User {assignedTo}")

    flash('Item successfully assigned', 'success')
    return redirect(request.referrer or url_for('admin'))


@app.route('/unassign-item', methods=['POST'])
def unassign_item():
    serial_number = request.form['serialNumber']

    items = Items.query.filter_by(SerialNumber=serial_number).first()
    if items:
        items.AssignedTo = None
        db.session.commit()
        
        logger.info(f"Item {serial_number} Unassigned")
        log_message(f"Item {serial_number} Unassigned")
        flash('Item successfully unassigned', 'success')
    else:
        flash('Item not found', 'error')

    # Redirect back to the referrer URL (the page where the request originated)
    return redirect(request.referrer or url_for('admin'))




@app.route('/edit-user', methods=['POST'])
def edit_user():
    uid = request.form['uid']
    full_name = request.form['fullName']
    email = request.form['email']
    is_admin = 1 if 'isAdmin' in request.form else 0

    user = User.query.get(uid)
    if user:
        user.FullName = full_name
        user.Email = email
        user.isAdmin = is_admin
        db.session.commit()
        
        logger.info(f"User Info Modified")
        log_message(f"User Info Modified")
        flash('User updated successfully!', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(request.referrer or url_for('admin'))


@app.route('/edit-item', methods=['POST'])
def edit_item():
    serial_number = request.form['editSerialNumber']  # Updated field name
    item_name = request.form['editItemName']  # Updated field name
    quantity = request.form['editQuantity']  # Updated field name
    category = request.form['editCategory']  # Updated field name
    bill_number = request.form['editBillNumber']  # Updated field name
    date_of_purchase = request.form['editDateOfPurchase']  # Updated field name
    warranty = request.form['editWarranty']  # Updated field name

    item = Items.query.get(serial_number)
    if item:
        item.ItemName = item_name
        item.Quantity = quantity
        item.Category = category
        item.BillNumber = bill_number
        item.DateOfPurchase = date_of_purchase
        item.Warranty = warranty
        db.session.commit()
        logger.info(f"Item Info Modified")
        log_message(f"Item Info Modified")
        flash('Item updated successfully!', 'success')
    else:
        flash('Item not found.', 'danger')

    return redirect(url_for('admin'))






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
    users = User.query.all()  # Retrieve all users
    
    if request.method == 'POST':
        print("Items Post Successful")
        
        # Retrieve form data
        serialNumber = request.form['serialNumber']
        itemName = request.form['itemName']
        quantity = request.form['quantity']
        category = request.form['category']
        billNumber = request.form['billNumber']
        dateOfPurchase = request.form['dateOfPurchase']
        warranty = request.form['warranty']
        assignedTo = request.form['assignedTo']
        
        # Create new item and add to the database
        new_item = Items(
            ItemName=itemName, 
            Quantity=quantity, 
            Category=category,
            BillNumber=billNumber, 
            DateOfPurchase=dateOfPurchase, 
            Warranty=warranty, 
            AssignedTo=assignedTo
        )
        db.session.add(new_item)
        db.session.commit()

    return render_template('admin.html', users=users)  # Ensure 'users' variable matches with the one in the template







if __name__ == '__main__':
    app.run(debug=True)



